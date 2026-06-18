import os
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Tuple

import joblib
import pandas as pd

CLASSIFIER_PATH = "models/traffic_classifier.pkl"
REGRESSOR_PATH = "models/traffic_regressor.pkl"
ENCODER_PATH = "models/label_encoder.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"
METADATA_PATH = "models/metadata.pkl"


def models_exist() -> bool:
    required_files = [
        CLASSIFIER_PATH,
        REGRESSOR_PATH,
        ENCODER_PATH,
        FEATURE_COLUMNS_PATH,
        METADATA_PATH,
    ]
    return all(os.path.exists(path) for path in required_files)


def get_metadata() -> dict:
    if not os.path.exists(METADATA_PATH):
        return {}
    return joblib.load(METADATA_PATH)


def _load_artifacts() -> Tuple[Any, Any, Any, List[str], dict]:
    if not models_exist():
        raise FileNotFoundError("Model artifacts not found. Run POST /train first.")

    clf = joblib.load(CLASSIFIER_PATH)
    reg = joblib.load(REGRESSOR_PATH)
    le = joblib.load(ENCODER_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
    metadata = get_metadata()
    return clf, reg, le, feature_columns, metadata


def _validate_inputs(route_id: int, day_of_week: int, hour: int, average_speed: float) -> None:
    if route_id <= 0:
        raise ValueError("route_id must be greater than 0")
    if day_of_week < 0 or day_of_week > 6:
        raise ValueError("day_of_week must be between 0 and 6")
    if hour < 0 or hour > 23:
        raise ValueError("hour must be between 0 and 23")
    if average_speed < 0:
        raise ValueError("average_speed must be >= 0")


def engineer_features(
    route_id: int,
    day_of_week: int,
    hour: int,
    average_speed: float = 40.0,
    month: int | None = None
) -> pd.DataFrame:
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

    if month is None:
        month = datetime.now().month

    is_weekend = int(day_of_week >= 5)
    is_business_day = int(day_of_week < 5)
    is_rush_hour = int((7 <= hour <= 10) or (16 <= hour <= 19))
    congestion_multiplier = 1.3 if is_rush_hour else 1.0
    traffic_ratio = 1.2 if is_rush_hour else 0.9
    speed_normalized = min(average_speed / 60.0, 1.0)
    hour_weekday_interaction = hour * day_of_week
    time_period = categorize_period(hour)

    return pd.DataFrame([{
        "route_id": route_id,
        "day_of_week": day_of_week,
        "hour": hour,
        "month": month,
        "average_speed": average_speed,
        "time_period": time_period,
        "is_weekend": is_weekend,
        "is_business_day": is_business_day,
        "is_rush_hour": is_rush_hour,
        "congestion_multiplier": congestion_multiplier,
        "traffic_ratio": traffic_ratio,
        "speed_normalized": speed_normalized,
        "hour_weekday_interaction": hour_weekday_interaction,
    }])


def _prepare_features_for_inference(
    route_id: int,
    day_of_week: int,
    hour: int,
    average_speed: float,
    feature_columns: List[str]
) -> pd.DataFrame:
    features_df = engineer_features(route_id, day_of_week, hour, average_speed)

    missing_columns = [col for col in feature_columns if col not in features_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required feature columns for inference: {missing_columns}")

    return features_df[feature_columns].copy()


def predict(
    route_id: int,
    day_of_week: int,
    hour: int,
    average_speed: float = 40.0
) -> Dict[str, Any]:
    _validate_inputs(route_id, day_of_week, hour, average_speed)

    clf, reg, le, feature_columns, metadata = _load_artifacts()
    features_df = _prepare_features_for_inference(
        route_id, day_of_week, hour, average_speed, feature_columns
    )

    level_encoded = clf.predict(features_df)[0]
    level_label = le.inverse_transform([level_encoded])[0]

    probabilities = clf.predict_proba(features_df)[0]
    confidence = float(max(probabilities))

    predicted_duration_seconds = float(reg.predict(features_df)[0])
    predicted_duration_seconds = max(predicted_duration_seconds, 0.0)
    predicted_duration_minutes = round(predicted_duration_seconds / 60.0, 1)

    is_peak_hour = bool(features_df.iloc[0]["is_rush_hour"])

    days_name = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    day_name = days_name[day_of_week]

    if level_label == "HIGH":
        recommendation = f"Alto tráfego esperado. Considere sair {30 + (10 if is_peak_hour else 0)} minutos antes."
    elif level_label == "MEDIUM":
        recommendation = "Tráfego moderado. Saída normal recomendada."
    else:
        recommendation = "Baixo tráfego esperado. Fluxo mais livre na rota."

    alternative_hours = None
    if is_peak_hour:
        if 7 <= hour <= 10:
            alternative_hours = [11, 12, 13]
        elif 16 <= hour <= 19:
            alternative_hours = [13, 14, 15]

    probability_distribution = {
        level: round(float(prob), 3)
        for level, prob in zip(le.classes_, probabilities)
    }

    return {
        "predicted_level": level_label,
        "predicted_duration": predicted_duration_minutes,
        "confidence": round(confidence, 2),
        "is_peak_hour": is_peak_hour,
        "day_of_week_name": day_name,
        "recommendation": recommendation,
        "alternative_hours": alternative_hours,
        "probability_distribution": probability_distribution,
        "model_version": metadata.get("model_version"),
    }


def predict_best_hours_range(
    route_id: int,
    day_of_week: int,
    start_hour: int = 6,
    end_hour: int = 23,
    average_speed: float = 40.0
) -> List[Dict[str, Any]]:
    _validate_inputs(route_id, day_of_week, start_hour, average_speed)
    _validate_inputs(route_id, day_of_week, end_hour, average_speed)

    if start_hour > end_hour:
        raise ValueError("start_hour must be less than or equal to end_hour")

    results = []

    for hour in range(start_hour, end_hour + 1):
        result = predict(route_id, day_of_week, hour, average_speed)
        results.append({
            "hour": hour,
            "level": result["predicted_level"],
            "duration": result["predicted_duration"],
            "confidence": result["confidence"],
            "is_peak": result["is_peak_hour"],
        })

    level_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    results.sort(key=lambda item: (level_order.get(item["level"], 99), item["duration"]))
    return results


def get_route_insights(route_id: int) -> Dict[str, Any]:
    if not models_exist():
        raise FileNotFoundError("Model artifacts not found.")

    if route_id <= 0:
        raise ValueError("route_id must be greater than 0")

    insights = {
        "route_id": route_id,
        "best_times": {},
        "worst_times": {},
        "peak_hours": [],
        "low_traffic_hours": [],
        "most_common_peak_hour": None,
        "most_common_low_traffic_hour": None,
    }

    days_name = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

    for day in range(7):
        results = predict_best_hours_range(route_id, day)

        if not results:
            insights["best_times"][days_name[day]] = []
            insights["worst_times"][days_name[day]] = []
            continue

        best_3 = results[:3]
        worst_3 = results[-3:]

        insights["best_times"][days_name[day]] = [item["hour"] for item in best_3]
        insights["worst_times"][days_name[day]] = [item["hour"] for item in worst_3]

        peak_hours = [item["hour"] for item in results if item["is_peak"]]
        low_traffic_hours = [item["hour"] for item in results if item["level"] == "LOW"]

        insights["peak_hours"].extend(peak_hours)
        insights["low_traffic_hours"].extend(low_traffic_hours)

    if insights["peak_hours"]:
        insights["most_common_peak_hour"] = Counter(insights["peak_hours"]).most_common(1)[0][0]

    if insights["low_traffic_hours"]:
        insights["most_common_low_traffic_hour"] = Counter(insights["low_traffic_hours"]).most_common(1)[0][0]

    return insights