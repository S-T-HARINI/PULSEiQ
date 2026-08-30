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
from ai.forecasting.models import ForecastTarget
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


def test_real_xgboost_model_loading():
    """Verify that the real pulseiq_xgboost_model.pkl loads safely."""
    from ai.forecasting.forecaster import DEFAULT_MODEL_PATH, load_trained_demand_model

    assert DEFAULT_MODEL_PATH.exists()
    model = load_trained_demand_model(DEFAULT_MODEL_PATH)
    assert model is not None
    assert hasattr(model, "predict")

    forecaster = DemandForecaster(seed=42)
    assert forecaster.using_real_model is True
    assert forecaster.is_fitted is True
    assert forecaster.trained_model is not None


def test_demand_forecaster_real_model_prediction():
    """Verify DemandForecaster produces realistic multi-step forecasts with the real trained model."""
    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    forecaster = DemandForecaster(seed=42)
    assert forecaster.using_real_model is True

    res = forecaster.predict(hospital_node, horizon_hours=24)
    assert res.target_id == "load_hospital_main"
    assert res.target_type == ForecastTarget.DEMAND
    assert res.horizon_hours == 24
    assert len(res.points) == 24
    assert res.peak_mw > 0
    assert res.total_mwh > 0
    assert res.model_name == "TrainedXGBoostModel"

    for pt in res.points:
        assert pt.confidence_lower <= pt.value_mw <= pt.confidence_upper
        assert pt.value_mw > 0


def test_demand_forecaster_synthetic_fallback():
    """Verify DemandForecaster seamlessly falls back to synthetic ML when .pkl model is unavailable."""
    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    forecaster = DemandForecaster(n_estimators=20, seed=42, model_path="nonexistent_pulseiq_model.pkl")
    assert forecaster.using_real_model is False
    assert forecaster.trained_model is None

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


@pytest.mark.parametrize("horizon", [24, 48, 72, 168])
def test_multi_horizon_demand_forecasting(horizon):
    """
    Verify DemandForecaster multi-horizon forecasting (24h, 48h, 72h, 168h):
    - Exact point counts
    - Continuous hourly timestamps
    - Non-negative predictions
    - Valid ForecastResult structure and recursive autoregression
    """
    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    forecaster = DemandForecaster(seed=42)
    res = forecaster.predict(hospital_node, horizon_hours=horizon)

    # 1. Exact point count
    assert res.horizon_hours == horizon
    assert len(res.points) == horizon
    assert res.target_id == "load_hospital_main"
    assert res.target_type == ForecastTarget.DEMAND

    # 2. Check summary metrics
    assert res.peak_mw > 0
    assert res.total_mwh > 0
    assert res.average_mw > 0

    # 3. Check continuous timestamps and non-negative values
    timestamps = [pd.to_datetime(pt.timestamp) for pt in res.points]
    for i in range(len(timestamps) - 1):
        delta = timestamps[i + 1] - timestamps[i]
        assert delta.total_seconds() == 3600, f"Timestamp gap between point {i} and {i+1} is not 1 hour: {delta}"

    for pt in res.points:
        assert pt.value_mw >= 0, f"Prediction is negative: {pt.value_mw}"
        assert pt.confidence_lower >= 0, f"Lower confidence bound is negative: {pt.confidence_lower}"
        assert pt.confidence_lower <= pt.value_mw <= pt.confidence_upper, "Confidence bounds inverted"


@pytest.mark.parametrize("horizon", [24, 48, 72, 168])
def test_multi_horizon_grid_forecaster_unified(horizon):
    """
    Verify GridForecaster orchestrates multi-horizon forecasts (24h, 48h, 72h, 168h)
    across all nodes with valid GridForecastSummary structures.
    """
    grid = create_mock_grid()
    grid_fc = GridForecaster(seed=42)
    summary = grid_fc.forecast_grid(grid, horizon_hours=horizon)

    assert summary.horizon_hours == horizon
    assert len(summary.timestamps) == horizon
    assert len(summary.total_demand_curve) == horizon
    assert len(summary.total_renewable_curve) == horizon
    assert len(summary.net_load_curve) == horizon
    assert summary.peak_net_load_mw >= 0
    assert summary.summary_metrics["total_demand_mwh"] > 0
    assert summary.summary_metrics["peak_gross_demand_mw"] > 0

    summary_dict = summary.to_dict()
    assert summary_dict["horizon_hours"] == horizon
    assert len(summary_dict["timestamps"]) == horizon
    assert len(summary_dict["total_demand_curve"]) == horizon
    assert "demand_forecasts" in summary_dict


