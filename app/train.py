"""
train.py
Treina o modelo XGBoost com os dados gerados para Aracaju/SE.
Features ricas: hora, dia, mês, rush, fim de semana, velocidade,
período do dia, interação hora×dia.
"""

import os
from datetime import datetime

import joblib
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier, XGBRegressor

load_dotenv()

CLASSIFIER_PATH    = "models/traffic_classifier.pkl"
REGRESSOR_PATH     = "models/traffic_regressor.pkl"
ENCODER_PATH       = "models/label_encoder.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"
METADATA_PATH      = "models/metadata.pkl"


def get_engine():
    from sqlalchemy import create_engine
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}"
        f":{os.getenv('DB_PASSWORD', '123')}"
        f"@{os.getenv('DB_HOST', 'localhost')}"
        f":{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'traffic')}"
    )
    return create_engine(url)


def fetch_data() -> pd.DataFrame:
    query = """
        SELECT
            td.route_id,
            EXTRACT(DOW   FROM td.timestamp)::int  AS day_of_week,
            EXTRACT(HOUR  FROM td.timestamp)::int  AS hour,
            EXTRACT(MONTH FROM td.timestamp)::int  AS month,
            td.average_speed,
            td.duration_in_traffic,
            td.traffic_level
        FROM traffic_data td
        JOIN route r ON r.id = td.route_id
        WHERE r.active = true
    """
    engine = get_engine()
    try:
        df = pd.read_sql(query, engine)
        return df
    finally:
        engine.dispose()


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cria features ricas a partir dos dados brutos.
    Deve ser IDÊNTICA à função em model.py.
    """
    result = df.copy()

    # Período do dia (7 períodos que refletem Aracaju)
    def time_period(h: int) -> int:
        if 0  <= h < 5:  return 0  # madrugada
        if 5  <= h < 7:  return 1  # início do dia
        if 7  <= h < 10: return 2  # rush matinal
        if 10 <= h < 12: return 3  # manhã
        if 12 <= h < 14: return 4  # almoço
        if 14 <= h < 17: return 5  # tarde
        if 17 <= h < 20: return 6  # rush noturno
        if 20 <= h < 22: return 7  # noite
        return 8                    # noite tarde

    result["time_period"]      = result["hour"].apply(time_period)
    result["is_weekend"]       = (result["day_of_week"] >= 5).astype(int)
    result["is_business_day"]  = (result["day_of_week"] < 5).astype(int)

    # Rush matinal (7h-9h) e noturno (17h-19h) — picos reais de Aracaju
    result["is_rush_hour"] = result["hour"].apply(
        lambda h: 1 if (7 <= h <= 9 or 17 <= h <= 19) else 0
    )

    # Mês de chuva (abr-ago em Aracaju)
    result["is_rainy_season"] = result["month"].apply(
        lambda m: 1 if m in [4, 5, 6, 7, 8] else 0
    )

    # Mês de férias (jan e jul = menos trânsito)
    result["is_vacation_month"] = result["month"].apply(
        lambda m: 1 if m in [1, 7] else 0
    )

    # Interações
    result["hour_x_weekday"]   = result["hour"] * result["day_of_week"]
    result["hour_x_rush"]      = result["hour"] * result["is_rush_hour"]
    result["speed_normalized"] = (result["average_speed"] / 60.0).clip(upper=1.0)

    # Congestionamento relativo
    result["congestion_index"] = result["hour"].apply(
        lambda h: 1.3 if (7 <= h <= 9 or 17 <= h <= 19) else
                  1.1 if (12 <= h <= 13) else 1.0
    )

    return result


FEATURE_COLUMNS = [
    "route_id",
    "day_of_week",
    "hour",
    "month",
    "average_speed",
    "time_period",
    "is_weekend",
    "is_business_day",
    "is_rush_hour",
    "is_rainy_season",
    "is_vacation_month",
    "hour_x_weekday",
    "hour_x_rush",
    "speed_normalized",
    "congestion_index",
]


def train_model():
    print("\n" + "=" * 60)
    print("TREINAMENTO DO MODELO — ARACAJU/SE")
    print("=" * 60)

    print("\n📦 Buscando dados do banco...")
    df = fetch_data()

    if len(df) < 100:
        raise ValueError(
            f"Dados insuficientes: {len(df)} registros. "
            f"Execute data/generate_data.py primeiro."
        )

    print(f"✅ {len(df):,} registros carregados")
    print(f"   Distribuição: {df['traffic_level'].value_counts().to_dict()}")

    # Feature engineering
    df = engineer_features(df)
    X  = df[FEATURE_COLUMNS]

    # --- Classificador (nível de tráfego: LOW / MEDIUM / HIGH) ---
    le      = LabelEncoder()
    y_level = le.fit_transform(df["traffic_level"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_level, test_size=0.2, random_state=42, stratify=y_level
    )
    y_dur_train = df["duration_in_traffic"].loc[X_train.index]
    y_dur_test  = df["duration_in_traffic"].loc[X_test.index]

    print(f"\n🤖 Treinando classificador XGBoost...")
    clf = XGBClassifier(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=3,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    y_pred   = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n🎯 Acurácia do classificador: {accuracy:.2%}")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # --- Regressor (duração em tráfego) ---
    print("🤖 Treinando regressor XGBoost...")
    reg = XGBRegressor(
        n_estimators=300,
        max_depth=7,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1,
    )
    reg.fit(X_train, y_dur_train)

    y_dur_pred = reg.predict(X_test)
    mae = mean_absolute_error(y_dur_test, y_dur_pred)
    r2  = r2_score(y_dur_test, y_dur_pred)

    print(f"   MAE: {mae:.1f} segundos ({mae/60:.1f} min)")
    print(f"   R²:  {r2:.4f}")

    # Salva modelos e metadados
    os.makedirs("models", exist_ok=True)
    joblib.dump(clf,            CLASSIFIER_PATH)
    joblib.dump(reg,            REGRESSOR_PATH)
    joblib.dump(le,             ENCODER_PATH)
    joblib.dump(FEATURE_COLUMNS, FEATURE_COLUMNS_PATH)

    metadata = {
        "trained_at":           datetime.now().isoformat(),
        "model_version":        "3.0.0",
        "total_samples":        len(df),
        "test_samples":         len(X_test),
        "feature_columns":      FEATURE_COLUMNS,
        "traffic_levels":       list(le.classes_),
        "classifier_accuracy":  float(accuracy),
        "regressor_mae":        float(mae),
        "regressor_r2":         float(r2),
        "region":               "Aracaju/SE",
    }
    joblib.dump(metadata, METADATA_PATH)

    print("\n💾 Modelos salvos em /models")
    print("=" * 60)

    return accuracy, len(df)