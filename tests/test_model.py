"""
test_model.py
Testes unitários para app/model.py
Execute com: pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_artifacts():
    """Simula os artefatos do modelo treinado."""
    clf = MagicMock()
    reg = MagicMock()
    le  = MagicMock()

    le.classes_              = np.array(["HIGH", "LOW", "MEDIUM"])
    clf.predict.return_value = np.array([1])           # LOW
    clf.predict_proba.return_value = np.array([[0.1, 0.8, 0.1]])
    reg.predict.return_value = np.array([1800.0])      # 30 minutos

    feature_columns = [
        "route_id", "day_of_week", "hour", "month", "average_speed",
        "time_period", "is_weekend", "is_business_day", "is_rush_hour",
        "is_rainy_season", "is_vacation_month", "hour_x_weekday",
        "hour_x_rush", "speed_normalized", "congestion_index",
    ]

    metadata = {
        "model_version": "3.0.0",
        "trained_at": "2024-01-01T00:00:00",
        "total_samples": 200000,
        "classifier_accuracy": 0.97,
    }

    le.inverse_transform.return_value = np.array(["LOW"])

    return clf, reg, le, feature_columns, metadata


# ---------------------------------------------------------------------------
# engineer_features
# ---------------------------------------------------------------------------

class TestEngineerFeatures:

    def test_returns_dataframe(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 8, 40.0)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_rush_hour_morning(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 8, 40.0)
        assert df.iloc[0]["is_rush_hour"] == 1

    def test_rush_hour_evening(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 18, 40.0)
        assert df.iloc[0]["is_rush_hour"] == 1

    def test_not_rush_hour(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 14, 40.0)
        assert df.iloc[0]["is_rush_hour"] == 0

    def test_weekend_saturday(self):
        from app.model import engineer_features
        df = engineer_features(1, 5, 10, 40.0)  # sábado
        assert df.iloc[0]["is_weekend"] == 1
        assert df.iloc[0]["is_business_day"] == 0

    def test_weekday(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 10, 40.0)  # segunda
        assert df.iloc[0]["is_weekend"] == 0
        assert df.iloc[0]["is_business_day"] == 1

    def test_rainy_season_june(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 10, 40.0, month=6)
        assert df.iloc[0]["is_rainy_season"] == 1

    def test_dry_season_november(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 10, 40.0, month=11)
        assert df.iloc[0]["is_rainy_season"] == 0

    def test_vacation_month_january(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 10, 40.0, month=1)
        assert df.iloc[0]["is_vacation_month"] == 1

    def test_speed_normalized_clipped(self):
        from app.model import engineer_features
        # Velocidade acima de 60 deve ser clampada em 1.0
        df = engineer_features(1, 1, 10, 120.0)
        assert df.iloc[0]["speed_normalized"] == 1.0

    def test_time_period_madrugada(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 2, 40.0)
        assert df.iloc[0]["time_period"] == 0

    def test_time_period_rush_matinal(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 8, 40.0)
        assert df.iloc[0]["time_period"] == 2

    def test_congestion_index_rush(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 8, 40.0)
        assert df.iloc[0]["congestion_index"] == 1.3

    def test_congestion_index_normal(self):
        from app.model import engineer_features
        df = engineer_features(1, 1, 15, 40.0)
        assert df.iloc[0]["congestion_index"] == 1.0


# ---------------------------------------------------------------------------
# _validate
# ---------------------------------------------------------------------------

class TestValidate:

    def test_invalid_route_id(self):
        from app.model import _validate
        with pytest.raises(ValueError, match="route_id"):
            _validate(0, 1, 8, 40.0)

    def test_invalid_day_of_week_negative(self):
        from app.model import _validate
        with pytest.raises(ValueError, match="day_of_week"):
            _validate(1, -1, 8, 40.0)

    def test_invalid_day_of_week_above_6(self):
        from app.model import _validate
        with pytest.raises(ValueError, match="day_of_week"):
            _validate(1, 7, 8, 40.0)

    def test_invalid_hour_negative(self):
        from app.model import _validate
        with pytest.raises(ValueError, match="hour"):
            _validate(1, 1, -1, 40.0)

    def test_invalid_hour_above_23(self):
        from app.model import _validate
        with pytest.raises(ValueError, match="hour"):
            _validate(1, 1, 24, 40.0)

    def test_invalid_speed(self):
        from app.model import _validate
        with pytest.raises(ValueError, match="average_speed"):
            _validate(1, 1, 8, -1.0)

    def test_valid_inputs(self):
        from app.model import _validate
        _validate(1, 0, 0, 0.0)   # não deve lançar


# ---------------------------------------------------------------------------
# predict
# ---------------------------------------------------------------------------

class TestPredict:

    def test_predict_returns_expected_keys(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 1, 8, 40.0)

        expected_keys = {
            "predicted_level", "predicted_duration", "confidence",
            "is_peak_hour", "day_of_week_name", "recommendation",
            "alternative_hours", "probability_distribution", "model_version",
        }
        assert expected_keys.issubset(result.keys())

    def test_predict_level_is_string(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 1, 8, 40.0)
        assert isinstance(result["predicted_level"], str)

    def test_predict_confidence_between_0_and_1(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 1, 8, 40.0)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_duration_positive(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 1, 8, 40.0)
        assert result["predicted_duration"] > 0

    def test_predict_day_name_segunda(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 0, 10, 40.0)  # day_of_week=0 → Segunda
        assert result["day_of_week_name"] == "Segunda"

    def test_predict_day_name_sabado(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 5, 10, 40.0)
        assert result["day_of_week_name"] == "Sábado"

    def test_predict_rush_hour_has_alternative_hours(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            result = predict(1, 1, 8, 40.0)   # rush matinal
        assert result["alternative_hours"] is not None
        assert len(result["alternative_hours"]) > 0

    def test_predict_no_models_raises_file_not_found(self):
        from app.model import predict
        with patch("app.model.models_exist", return_value=False):
            with pytest.raises(FileNotFoundError):
                predict(1, 1, 8, 40.0)

    def test_predict_invalid_route_id_raises_value_error(self, mock_artifacts):
        from app.model import predict
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            with pytest.raises(ValueError):
                predict(0, 1, 8, 40.0)


# ---------------------------------------------------------------------------
# predict_best_hours_range
# ---------------------------------------------------------------------------

class TestPredictBestHoursRange:

    def test_returns_sorted_by_level(self, mock_artifacts):
        from app.model import predict_best_hours_range
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            results = predict_best_hours_range(1, 1, 6, 10)

        assert len(results) == 5   # 6,7,8,9,10
        levels = [r["level"] for r in results]
        order  = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        assert levels == sorted(levels, key=lambda l: order[l])

    def test_all_hours_present(self, mock_artifacts):
        from app.model import predict_best_hours_range
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            results = predict_best_hours_range(1, 1, 8, 10)

        hours = {r["hour"] for r in results}
        assert hours == {8, 9, 10}

    def test_invalid_start_hour(self, mock_artifacts):
        from app.model import predict_best_hours_range
        with patch("app.model._load_artifacts", return_value=mock_artifacts):
            with pytest.raises(ValueError):
                predict_best_hours_range(1, 1, 25, 23)