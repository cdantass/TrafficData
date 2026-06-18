import os
from datetime import datetime

import joblib
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier, XGBRegressor

load_dotenv()

CLASSIFIER_PATH = "models/traffic_classifier.pkl"
REGRESSOR_PATH = "models/traffic_regressor.pkl"
ENCODER_PATH = "models/label_encoder.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"
METADATA_PATH = "models/metadata.pkl"


def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}"
        f":{os.getenv('DB_PASSWORD', '123')}"
        f"@{os.getenv('DB_HOST', 'localhost')}"
        f":{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'traffic')}"
    )
    return create_engine(url)


def fetch_data():
    query = """
        SELECT
            td.route_id,
            EXTRACT(DOW FROM td.timestamp)::int AS day_of_week,
            EXTRACT(HOUR FROM td.timestamp)::int AS hour,
            EXTRACT(MONTH FROM td.timestamp)::int AS month,
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


def engineer_features_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    def categorize_period(h: int) -> int:
        if 6 <= h < 9:
            return 0
        if 9 <= h < 11:
            return 1
        if 11 <= h < 13:
            return 2
        if 13 <= h < 15:
            return 3
        if 15 <= h < 18:
            return 4
        if 18 <= h < 20:
            return 5
        return 6

    result["time_period"] = result["hour"].apply(categorize_period)
    result["is_weekend"] = (result["day_of_week"] >= 5).astype(int)
    result["is_business_day"] = (result["day_of_week"] < 5).astype(int)
    result["is_rush_hour"] = result["hour"].apply(
        lambda h: 1 if (7 <= h <= 10 or 16 <= h <= 19) else 0
    )
    result["congestion_multiplier"] = result["hour"].apply(
        lambda h: 1.3 if (7 <= h <= 10 or 16 <= h <= 19) else 1.0
    )
    result["traffic_ratio"] = result["hour"].apply(
        lambda h: 1.2 if (7 <= h <= 10 or 16 <= h <= 19) else 0.9
    )
    result["speed_normalized"] = (result["average_speed"] / 60.0).clip(upper=1.0)
    result["hour_weekday_interaction"] = result["hour"] * result["day_of_week"]

    return result


def train_model():
    print("📦 Buscando dados...")
    df = fetch_data()

    if len(df) < 50:
        raise ValueError(f"Dados insuficientes: {len(df)} registros. Mínimo: 50")

    print(f"✅ {len(df)} registros carregados")

    df = engineer_features_dataframe(df)

    feature_columns = [
        "route_id",
        "day_of_week",
        "hour",
        "month",
        "average_speed",
        "time_period",
        "is_weekend",
        "is_business_day",
        "is_rush_hour",
        "congestion_multiplier",
        "traffic_ratio",
        "speed_normalized",
        "hour_weekday_interaction"
    ]

    X = df[feature_columns]

    le = LabelEncoder()
    y_level = le.fit_transform(df["traffic_level"])
    y_duration = df["duration_in_traffic"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_level, test_size=0.2, random_state=42, stratify=y_level
    )

    y_duration_train = y_duration.loc[X_train.index]
    y_duration_test = y_duration.loc[X_test.index]

    clf = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        eval_metric="mlogloss",
        random_state=42
    )
    clf.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"🎯 Acurácia: {accuracy:.2%}")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    reg = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42
    )
    reg.fit(X_train, y_duration_train)

    y_duration_pred = reg.predict(X_test)
    mae = mean_absolute_error(y_duration_test, y_duration_pred)
    r2 = r2_score(y_duration_test, y_duration_pred)

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, CLASSIFIER_PATH)
    joblib.dump(reg, REGRESSOR_PATH)
    joblib.dump(le, ENCODER_PATH)
    joblib.dump(feature_columns, FEATURE_COLUMNS_PATH)

    metadata = {
        "trained_at": datetime.now().isoformat(),
        "model_version": "2.0.0",
        "total_samples": len(df),
        "test_samples": len(X_test),
        "feature_columns": feature_columns,
        "traffic_levels": list(le.classes_),
        "classifier_accuracy": float(accuracy),
        "regressor_mae": float(mae),
        "regressor_r2": float(r2),
    }
    joblib.dump(metadata, METADATA_PATH)

    print("💾 Modelos salvos!")
    return accuracy, len(df)