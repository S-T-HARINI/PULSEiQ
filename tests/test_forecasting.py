"""
Unit tests for PULSEiQ Machine Learning Forecasting Module.
"""

import pytest
import numpy as np
import pandas as pd

from ai.forecasting import (
    DemandForecaster,
    GridForecaster,
    SolarForecaster,
    WindForecaster,
    generate_synthetic_load_dataset,
    generate_synthetic_solar_dataset,
    generate_synthetic_weather,
    generate_synthetic_wind_dataset,
)
from ai.forecasting.models import ForecastResult, ForecastTarget, TimeSeriesPoint
from ai.models.grid import NodeType
from ai.models.mock_grid import create_mock_grid


def test_synthetic_generators():
    """Verify synthetic weather and asset telemetry generation."""
    weather = generate_synthetic_weather(hours=48, seed=42)
    assert len(weather) == 48
    assert "temperature_c" in weather.columns
    assert "solar_irradiance_wm2" in weather.columns
    assert "wind_speed_mps" in weather.columns

    # Load series
    load_df = generate_synthetic_load_dataset("load_test", NodeType.LOAD_NORMAL, base_demand_mw=30.0, hours=48)
    assert len(load_df) == 48
    assert "target_demand_mw" in load_df.columns
    assert all(load_df["target_demand_mw"] > 0)

    # Solar series
    solar_df = generate_synthetic_solar_dataset("solar_test", capacity_mw=45.0, hours=48)
    assert len(solar_df) == 48
    assert max(solar_df["target_generation_mw"]) <= 45.0
    assert min(solar_df["target_generation_mw"]) == 0.0

    # Wind series
    wind_df = generate_synthetic_wind_dataset("wind_test", capacity_mw=50.0, hours=48)
    assert len(wind_df) == 48
    assert max(wind_df["target_generation_mw"]) <= 50.0


def test_demand_forecaster():
    """Verify DemandForecaster training, prediction, and confidence intervals."""
    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    forecaster = DemandForecaster(n_estimators=30, seed=42)
    res = forecaster.predict(hospital_node, horizon_hours=24)

    assert res.target_id == "load_hospital_main"
    assert res.target_type == ForecastTarget.DEMAND
    assert res.horizon_hours == 24
    assert len(res.points) == 24
    assert res.peak_mw > 0
    assert res.total_mwh > 0

    for pt in res.points:
        assert pt.confidence_lower <= pt.value_mw <= pt.confidence_upper
        assert pt.value_mw > 0


def test_solar_and_wind_forecaster():
    """Verify Solar and Wind generation forecasters."""
    grid = create_mock_grid()
    solar_node = grid.get_node("solar_farm_01")
    wind_node = grid.get_node("wind_farm_01")

    solar_fc = SolarForecaster(n_estimators=30, seed=42)
    solar_res = solar_fc.predict(solar_node, horizon_hours=24)
    assert solar_res.target_type == ForecastTarget.SOLAR
    assert len(solar_res.points) == 24
    # Night hours should be zero
    assert solar_res.points[0].value_mw == 0.0

    wind_fc = WindForecaster(n_estimators=30, seed=42)
    wind_res = wind_fc.predict(wind_node, horizon_hours=24)
    assert wind_res.target_type == ForecastTarget.WIND
    assert len(wind_res.points) == 24
    assert all(p.value_mw <= 50.0 for p in wind_res.points)


def test_grid_forecaster_unified():
    """Verify unified multi-asset grid forecasting."""
    grid = create_mock_grid()
    grid_fc = GridForecaster(seed=42)
    summary = grid_fc.forecast_grid(grid, horizon_hours=24)

    assert summary.horizon_hours == 24
    assert len(summary.total_demand_curve) == 24
    assert len(summary.total_renewable_curve) == 24
    assert len(summary.net_load_curve) == 24
    assert summary.peak_net_load_mw > 0
    assert "total_demand_mwh" in summary.summary_metrics
    assert "renewable_penetration_pct" in summary.summary_metrics

    # Test serialization
    summary_dict = summary.to_dict()
    assert "demand_forecasts" in summary_dict
    assert "solar_forecasts" in summary_dict
    assert "wind_forecasts" in summary_dict


def test_saved_model_artifact_loading():
    """Verify that demand_model.joblib and model_metadata.json exist and are readable."""
    import os
    import json
    import joblib
    from ai.forecasting.forecaster import DEFAULT_DEMAND_MODEL_PATH, DEFAULT_METADATA_PATH

    assert os.path.exists(DEFAULT_DEMAND_MODEL_PATH), f"Model artifact missing at {DEFAULT_DEMAND_MODEL_PATH}"
    assert os.path.exists(DEFAULT_METADATA_PATH), f"Metadata missing at {DEFAULT_METADATA_PATH}"

    model = joblib.load(DEFAULT_DEMAND_MODEL_PATH)
    assert hasattr(model, "predict"), "Loaded model must have a predict method"

    with open(DEFAULT_METADATA_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "feature_columns" in meta
    assert len(meta["feature_columns"]) == 23
    assert meta["model_name"] == "HistGradientBoostingRegressor"
    assert "test_metrics" in meta
    assert meta["test_metrics"]["mae"] > 0


def test_demand_forecaster_uses_trained_model():
    """Verify DemandForecaster automatically uses the trained model when artifact exists."""
    forecaster = DemandForecaster(seed=42)

    assert forecaster.is_trained_model is True
    assert forecaster.model_loaded is True
    assert forecaster.is_fitted is True
    assert forecaster.model_name == "HistGradientBoostingRegressor-trained"
    assert len(forecaster.feature_columns) == 23
    assert forecaster.training_mae > 0.0
    assert forecaster.training_rmse > 0.0


def test_trained_model_24h_multi_step_inference():
    """Verify 24-hour multi-step forecasting with dynamic autoregressive variation."""
    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    forecaster = DemandForecaster(seed=42)
    res = forecaster.predict(hospital_node, horizon_hours=24)

    assert res.target_id == "load_hospital_main"
    assert res.target_type == ForecastTarget.DEMAND
    assert res.horizon_hours == 24
    assert len(res.points) == 24
    assert res.model_name == "HistGradientBoostingRegressor-trained"

    # All values positive and non-negative
    values = [pt.value_mw for pt in res.points]
    assert all(v > 0 for v in values)
    assert res.peak_mw == max(values)
    assert res.min_mw == min(values)
    assert round(res.average_mw, 2) == round(sum(values) / len(values), 2)
    assert round(res.total_mwh, 2) == round(sum(values), 2)

    # Valid confidence bounds
    for pt in res.points:
        assert pt.confidence_lower <= pt.value_mw <= pt.confidence_upper
        assert pt.confidence_lower >= 0.0

    # Ensure predictions are genuinely dynamic across the 24 hours (not constant/flat)
    unique_values = set(round(v, 2) for v in values)
    assert len(unique_values) >= 10, f"Expected dynamic curve, got {len(unique_values)} unique values"

    # Verify metrics included
    assert "mae" in res.metrics
    assert "rmse" in res.metrics
    assert "r2" in res.metrics


def test_demand_forecaster_fallback_when_artifact_missing():
    """Verify clean backward-compatible fallback when model artifact is unavailable."""
    forecaster = DemandForecaster(
        model_path="non_existent_model_file.joblib",
        auto_load_artifact=False,
        seed=42,
    )

    assert forecaster.is_trained_model is False
    assert forecaster.model_loaded is False

    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    # Should not crash, falls back to synthetic fitting
    res = forecaster.predict(hospital_node, horizon_hours=24)
    assert res.target_id == "load_hospital_main"
    assert len(res.points) == 24
    assert res.peak_mw > 0
    assert all(pt.value_mw > 0 for pt in res.points)
    assert res.model_name in ("XGBoostRegressor", "GradientBoostingRegressor")


def test_forecast_result_serialization_roundtrip():
    """Verify full serialization roundtrip for ForecastResult with trained model output."""
    grid = create_mock_grid()
    node = grid.get_node("load_residential_north")

    forecaster = DemandForecaster(seed=42)
    res = forecaster.predict(node, horizon_hours=24)

    res_dict = res.to_dict()
    assert res_dict["model_name"] == "HistGradientBoostingRegressor-trained"
    assert len(res_dict["points"]) == 24
    assert "metrics" in res_dict

    restored = ForecastResult.from_dict(res_dict)
    assert restored.target_id == res.target_id
    assert restored.horizon_hours == 24
    assert restored.model_name == res.model_name
    assert len(restored.points) == 24
    assert restored.points[0].value_mw == res.points[0].value_mw

