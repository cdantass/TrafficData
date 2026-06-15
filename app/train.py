import os
from datetime import datetime
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingRegressor, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
    r2_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder


load_dotenv()


MODELS_DIR = "models"
CSV_FALLBACK_PATH = "data/traffic_data.csv"

CLASSIFIER_PATH = os.path.join(MODELS_DIR, "traffic_classifier.pkl")
REGRESSOR_PATH = os.path.join(MODELS_DIR, "traffic_regressor.pkl")
ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.pkl")
FEATURE_COLUMNS_PATH = os.path.join(MODELS_DIR, "feature_columns.pkl")
METADATA_PATH = os.path.join(MODELS_DIR, "metadata.pkl")


def fetch_data_from_db() -> pd.DataFrame:
    """
    Busca dados do PostgreSQL.
    Se falhar, usa o CSV local como fallback.
    """
    query = """
        SELECT
            td.route_id,
            EXTRACT(DOW FROM td.timestamp)::int  AS day_of_week,
            EXTRACT(HOUR FROM td.timestamp)::int AS hour,
            td.duration,
            td.duration_in_traffic,
            td.average_speed,
            td.traffic_level
        FROM traffic_data td
        WHERE td.route_id IS NOT NULL
          AND td.timestamp IS NOT NULL
          AND td.duration IS NOT NULL
          AND td.duration_in_traffic IS NOT NULL
          AND td.average_speed IS NOT NULL
          AND td.traffic_level IS NOT NULL
        ORDER BY td.timestamp DESC
    """

    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "traffic"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "2005"),
            connect_timeout=30,
        )

        df = pd.read_sql(query, conn)
        conn.close()
        print("✅ Dados carregados do PostgreSQL")
        return df

    except Exception as e:
        print(f"⚠️ Não foi possível conectar ao PostgreSQL: {e}")
        print("📁 Carregando dados do CSV local...")

        if not os.path.exists(CSV_FALLBACK_PATH):
            raise FileNotFoundError(
                f"CSV fallback não encontrado em: {CSV_FALLBACK_PATH}"
            )

        df = pd.read_csv(CSV_FALLBACK_PATH)
        print(f"✅ {len(df)} registros carregados do CSV")
        return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante que o dataframe tenha as colunas mínimas esperadas.
    """
    df = df.copy()

    expected_columns = {
        "route_id",
        "day_of_week",
        "hour",
        "duration",
        "duration_in_traffic",
        "average_speed",
        "traffic_level",
    }

    missing = expected_columns - set(df.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {sorted(missing)}")

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa dados inválidos e padroniza tipos.
    """
    df = df.copy()

    numeric_columns = [
        "route_id",
        "day_of_week",
        "hour",
        "duration",
        "duration_in_traffic",
        "average_speed",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["traffic_level"] = df["traffic_level"].astype(str).str.upper().str.strip()

    df = df.dropna(
        subset=[
            "route_id",
            "day_of_week",
            "hour",
            "duration",
            "duration_in_traffic",
            "average_speed",
            "traffic_level",
        ]
    )

    df = df[df["route_id"] > 0]
    df = df[df["day_of_week"].between(0, 6)]
    df = df[df["hour"].between(0, 23)]
    df = df[df["duration"] > 0]
    df = df[df["duration_in_traffic"] >= 0]
    df = df[df["average_speed"] >= 0]

    valid_levels = {"LOW", "MEDIUM", "HIGH"}
    df = df[df["traffic_level"].isin(valid_levels)]

    df = df.reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engenharia de features alinhada com a inferência em app/model.py.
    IMPORTANTE: este método deve permanecer sincronizado com engineer_features() do model.py
    """
    df = df.copy()

    def categorize_period(hour: int) -> int:
        if 6 <= hour < 9:
            return 0
        if 9 <= hour < 11:
            return 1
        if 11 <= hour < 13:
            return 2
        if 13 <= hour < 15:
            return 3
        if 15 <= hour < 18:
            return 4
        if 18 <= hour < 20:
            return 5
        return 6

    df["time_period"] = df["hour"].apply(categorize_period)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_business_day"] = (df["day_of_week"] < 5).astype(int)

    df["congestion_multiplier"] = np.where(
        (df["hour"].between(7, 10)) | (df["hour"].between(16, 19)),
        1.3,
        1.0
    )

    # Mantido para compatibilidade com o model.py atual
    df["traffic_ratio"] = np.where(
        (df["hour"].between(7, 10)) | (df["hour"].between(16, 19)),
        1.2,
        0.9
    )

    max_speed = max(float(df["average_speed"].max()), 1.0)
    df["speed_normalized"] = df["average_speed"] / max_speed
    df["hour_weekday_interaction"] = df["hour"] * df["day_of_week"]

    return df


def train_model() -> Tuple[float, int]:
    """
    Treina os modelos de classificação e regressão.
    Retorna:
        (accuracy, total_samples)
    """
    print("\n" + "=" * 60)
    print("🚀 TREINAMENTO DO MODELO DE TRÁFEGO")
    print("=" * 60)

    print("\n📦 Buscando dados...")
    df = fetch_data_from_db()
    df = normalize_columns(df)
    df = clean_data(df)

    if len(df) < 10:
        raise ValueError(f"Dados insuficientes para treino: {len(df)} registros. Mínimo: 10")

    print(f"✅ {len(df)} registros válidos carregados")

    print("\n🔧 Aplicando feature engineering...")
    df = engineer_features(df)

    feature_columns = [
        "route_id",
        "day_of_week",
        "hour",
        "average_speed",
        "time_period",
        "is_weekend",
        "is_business_day",
        "congestion_multiplier",
        "traffic_ratio",
        "speed_normalized",
        "hour_weekday_interaction",
    ]

    X = df[feature_columns].fillna(0)

    le = LabelEncoder()
    y_level = le.fit_transform(df["traffic_level"])

    print(f"   📊 Features: {feature_columns}")
    print(f"   🎯 Classes: {list(le.classes_)}")

    # Split estratificado para classificação
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_level,
        test_size=0.2,
        random_state=42,
        stratify=y_level
    )

    print("\n📈 Treinando RandomForestClassifier (nível de tráfego)...")
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"   ✅ Acurácia holdout: {accuracy:.2%}")
    print("\n   📋 Relatório de Classificação:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Cross-validation para reduzir ilusão de overfitting
    cv_folds = min(5, len(df))
    if cv_folds >= 3:
        cv_scores = cross_val_score(clf, X, y_level, cv=cv_folds, scoring="accuracy")
        cv_mean = float(cv_scores.mean())
        cv_std = float(cv_scores.std())
        print(f"\n   🔁 Cross-validation ({cv_folds} folds): {cv_mean:.2%} ± {cv_std:.2%}")
    else:
        cv_mean = None
        cv_std = None
        print("\n   ⚠️ Poucos dados para cross-validation confiável")

    feature_importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": clf.feature_importances_
    }).sort_values("importance", ascending=False)

    print("\n   🏆 Top 5 features mais importantes:")
    for _, row in feature_importance.head(5).iterrows():
        print(f"      {row['feature']}: {row['importance']:.4f}")

    print("\n📈 Treinando GradientBoostingRegressor (duração em tráfego)...")

    y_duration = df["duration_in_traffic"]

    X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(
        X,
        y_duration,
        test_size=0.2,
        random_state=42
    )

    reg = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )
    reg.fit(X_train_reg, y_train_reg)

    y_pred_reg = reg.predict(X_test_reg)
    mae = mean_absolute_error(y_test_reg, y_pred_reg)
    r2 = r2_score(y_test_reg, y_pred_reg)

    print(f"   ✅ MAE: {mae:.2f} segundos")
    print(f"   ✅ R² Score: {r2:.4f}")

    os.makedirs(MODELS_DIR, exist_ok=True)

    print("\n💾 Salvando modelos...")
    joblib.dump(clf, CLASSIFIER_PATH)
    joblib.dump(reg, REGRESSOR_PATH)
    joblib.dump(le, ENCODER_PATH)
    joblib.dump(feature_columns, FEATURE_COLUMNS_PATH)

    metadata = {
        "trained_at": datetime.now().isoformat(),
        "model_version": "2.1.0",
        "total_samples": int(len(df)),
        "test_samples": int(len(y_test)),
        "classifier_accuracy": float(accuracy),
        "classifier_cv_mean": cv_mean,
        "classifier_cv_std": cv_std,
        "regressor_mae": float(mae),
        "regressor_r2": float(r2),
        "traffic_levels": list(le.classes_),
        "feature_columns": feature_columns,
        "top_features": feature_importance.head(5).to_dict(orient="records"),
    }
    joblib.dump(metadata, METADATA_PATH)

    print("   ✅ Modelos salvos em /models")

    print("\n" + "=" * 60)
    print("✨ TREINAMENTO CONCLUÍDO COM SUCESSO")
    print(f"   📊 Amostras totais: {len(df)}")
    print(f"   🎯 Acurácia do classificador: {accuracy:.2%}")
    if cv_mean is not None:
        print(f"   🔁 CV média: {cv_mean:.2%} ± {cv_std:.2%}")
    print(f"   ⏱️  MAE do regressor: {mae:.2f}s")
    print("=" * 60 + "\n")

    return accuracy, len(df)


if __name__ == "__main__":
    train_model()