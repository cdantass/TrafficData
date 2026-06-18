"""
model.py
Inferência do modelo treinado para Aracaju/SE.
As features DEVEM ser idênticas às do train.py.
"""

import os
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import joblib
import pandas as pd

CLASSIFIER_PATH      = "models/traffic_classifier.pkl"
REGRESSOR_PATH       = "models/traffic_regressor.pkl"
ENCODER_PATH         = "models/label_encoder.pkl"
FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"
METADATA_PATH        = "models/metadata.pkl"


def models_exist() -> bool:
    return all(os.path.exists(p) for p in [
        CLASSIFIER_PATH, REGRESSOR_PATH,
        ENCODER_PATH, FEATURE_COLUMNS_PATH, METADATA_PATH,
    ])


def get_metadata() -> dict:
    if not os.path.exists(METADATA_PATH):
        return {}
    return joblib.load(METADATA_PATH)


def _load_artifacts():
    if not models_exist():
        raise FileNotFoundError("Modelos não encontrados. Execute POST /train primeiro.")
    clf            = joblib.load(CLASSIFIER_PATH)
    reg            = joblib.load(REGRESSOR_PATH)
    le             = joblib.load(ENCODER_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
    metadata       = get_metadata()
    return clf, reg, le, feature_columns, metadata


def _validate(route_id: int, day_of_week: int, hour: int, average_speed: float):
    if route_id <= 0:
        raise ValueError("route_id deve ser maior que 0")
    if not (0 <= day_of_week <= 6):
        raise ValueError("day_of_week deve ser entre 0 (Segunda) e 6 (Domingo)")
    if not (0 <= hour <= 23):
        raise ValueError("hour deve ser entre 0 e 23")
    if average_speed < 0:
        raise ValueError("average_speed deve ser >= 0")


def engineer_features(
    route_id: int,
    day_of_week: int,
    hour: int,
    average_speed: float = 40.0,
    month: Optional[int] = None,
) -> pd.DataFrame:
    """
    Espelho EXATO do engineer_features do train.py.
    Qualquer alteração aqui deve ser replicada lá, e vice-versa.
    """
    if month is None:
        month = datetime.now().month

    def time_period(h: int) -> int:
        if 0  <= h < 5:  return 0
        if 5  <= h < 7:  return 1
        if 7  <= h < 10: return 2
        if 10 <= h < 12: return 3
        if 12 <= h < 14: return 4
        if 14 <= h < 17: return 5
        if 17 <= h < 20: return 6
        if 20 <= h < 22: return 7
        return 8

    is_weekend        = int(day_of_week >= 5)
    is_business_day   = int(day_of_week < 5)
    is_rush_hour      = int(7 <= hour <= 9 or 17 <= hour <= 19)
    is_rainy_season   = int(month in [4, 5, 6, 7, 8])
    is_vacation_month = int(month in [1, 7])
    hour_x_weekday    = hour * day_of_week
    hour_x_rush       = hour * is_rush_hour
    speed_normalized  = min(average_speed / 60.0, 1.0)
    congestion_index  = (
        1.3 if (7 <= hour <= 9 or 17 <= hour <= 19) else
        1.1 if (12 <= hour <= 13) else 1.0
    )

    return pd.DataFrame([{
        "route_id":           route_id,
        "day_of_week":        day_of_week,
        "hour":               hour,
        "month":              month,
        "average_speed":      average_speed,
        "time_period":        time_period(hour),
        "is_weekend":         is_weekend,
        "is_business_day":    is_business_day,
        "is_rush_hour":       is_rush_hour,
        "is_rainy_season":    is_rainy_season,
        "is_vacation_month":  is_vacation_month,
        "hour_x_weekday":     hour_x_weekday,
        "hour_x_rush":        hour_x_rush,
        "speed_normalized":   speed_normalized,
        "congestion_index":   congestion_index,
    }])


def predict(
    route_id: int,
    day_of_week: int,
    hour: int,
    average_speed: float = 40.0,
) -> Dict[str, Any]:
    _validate(route_id, day_of_week, hour, average_speed)
    clf, reg, le, feature_columns, metadata = _load_artifacts()

    X = engineer_features(route_id, day_of_week, hour, average_speed)[feature_columns]

    level_encoded  = clf.predict(X)[0]
    level_label    = le.inverse_transform([level_encoded])[0]
    probabilities  = clf.predict_proba(X)[0]
    confidence     = float(max(probabilities))

    duration_sec = float(max(reg.predict(X)[0], 0.0))
    duration_min = round(duration_sec / 60.0, 1)

    is_rush = bool(X.iloc[0]["is_rush_hour"])

    days_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    day_name = days_pt[day_of_week]

    if level_label == "HIGH":
        extra = 30 + (15 if is_rush else 0)
        recommendation = f"Alto tráfego esperado. Considere sair {extra} minutos antes ou usar rotas alternativas."
    elif level_label == "MEDIUM":
        recommendation = "Tráfego moderado. Saída no horário normal, mas fique atento."
    else:
        recommendation = "Baixo tráfego previsto. Bom momento para circular."

    alternative_hours = None
    if is_rush:
        if 7 <= hour <= 9:
            alternative_hours = [10, 11, 13]
        elif 17 <= hour <= 19:
            alternative_hours = [14, 15, 20]

    return {
        "predicted_level":          level_label,
        "predicted_duration":       duration_min,
        "confidence":               round(confidence, 2),
        "is_peak_hour":             is_rush,
        "day_of_week_name":         day_name,
        "recommendation":           recommendation,
        "alternative_hours":        alternative_hours,
        "probability_distribution": {
            lvl: round(float(p), 3)
            for lvl, p in zip(le.classes_, probabilities)
        },
        "model_version": metadata.get("model_version", "3.0.0"),
    }


def predict_best_hours_range(
    route_id: int,
    day_of_week: int,
    start_hour: int = 6,
    end_hour: int = 23,
    average_speed: float = 40.0,
) -> List[Dict[str, Any]]:
    _validate(route_id, day_of_week, start_hour, average_speed)

    results = []
    for hour in range(start_hour, end_hour + 1):
        r = predict(route_id, day_of_week, hour, average_speed)
        results.append({
            "hour":       hour,
            "level":      r["predicted_level"],
            "duration":   r["predicted_duration"],
            "confidence": r["confidence"],
            "is_peak":    r["is_peak_hour"],
        })

    order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    results.sort(key=lambda x: (order.get(x["level"], 9), x["duration"]))
    return results


def get_route_insights(route_id: int) -> Dict[str, Any]:
    if not models_exist():
        raise FileNotFoundError("Modelos não encontrados.")
    if route_id <= 0:
        raise ValueError("route_id deve ser maior que 0.")

    days_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    insights: Dict[str, Any] = {
        "route_id":                    route_id,
        "best_times":                  {},
        "worst_times":                 {},
        "peak_hours":                  [],
        "low_traffic_hours":           [],
        "most_common_peak_hour":       None,
        "most_common_low_traffic_hour": None,
    }

    for day in range(7):
        results = predict_best_hours_range(route_id, day)
        name    = days_pt[day]

        insights["best_times"][name]  = [r["hour"] for r in results[:3]]
        insights["worst_times"][name] = [r["hour"] for r in results[-3:]]
        insights["peak_hours"].extend(r["hour"] for r in results if r["is_peak"])
        insights["low_traffic_hours"].extend(
            r["hour"] for r in results if r["level"] == "LOW"
        )

    if insights["peak_hours"]:
        insights["most_common_peak_hour"] = (
            Counter(insights["peak_hours"]).most_common(1)[0][0]
        )
    if insights["low_traffic_hours"]:
        insights["most_common_low_traffic_hour"] = (
            Counter(insights["low_traffic_hours"]).most_common(1)[0][0]
        )

    return insights