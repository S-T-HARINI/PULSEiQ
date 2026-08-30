"""
Unit tests for PULSEiQ Forecasting Model Evaluation and Baseline Benchmarking.
Verifies chronological time-series evaluation comparing the real trained XGBoost model
against previous-hour (Lag 1), same-hour previous-day (Lag 24), and same-hour previous-week (Lag 168) baselines.
"""

import numpy as np
import pandas as pd
import pytest

from ai.forecasting.evaluation import (
    ForecastingEvaluationResult,
    ModelEvaluationMetrics,
    calculate_metrics,
    evaluate_chronological_demand_models,
)
from ai.forecasting.forecaster import DemandForecaster
from ai.forecasting.generators import generate_synthetic_load_dataset
from ai.models.grid import NodeType


def test_calculate_metrics_basic():
    """Verify regression metric calculations (MAE, RMSE, MAPE, R2)."""
    y_true = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    y_pred = np.array([12.0, 19.0, 31.0, 38.0, 52.0])

    metrics = calculate_metrics(y_true, y_pred, "TestModel")

    # Expected MAE = (2 + 1 + 1 + 2 + 2) / 5 = 8 / 5 = 1.6
    assert isinstance(metrics, ModelEvaluationMetrics)
    assert np.isclose(metrics.mae, 1.6, atol=1e-3)
    assert metrics.rmse > metrics.mae
    assert metrics.mape_pct > 0.0
    assert 0.0 < metrics.r2_score <= 1.0
    assert metrics.sample_count == 5


def test_chronological_baselines_calculation():
    """Verify baseline predictions match exact chronological lags (Lag 1, Lag 24, Lag 168)."""
    total_hours = 336  # 2 weeks
    df = generate_synthetic_load_dataset(
        node_id="load_test_eval",
        node_type=NodeType.LOAD_NORMAL,
        base_demand_mw=40.0,
        hours=total_hours,
        seed=42,
    )

    eval_res = evaluate_chronological_demand_models(df=df, total_hours=total_hours, seed=42)

    assert isinstance(eval_res, ForecastingEvaluationResult)
    assert eval_res.evaluation_hours == total_hours - 168

    # Baseline metrics must be valid positive numbers
    for bm in [
        eval_res.baseline_previous_hour,
        eval_res.baseline_same_hour_prev_day,
        eval_res.baseline_same_hour_prev_week,
        eval_res.xgboost_model,
    ]:
        assert isinstance(bm.mae, float) and bm.mae > 0.0
        assert isinstance(bm.rmse, float) and bm.rmse > 0.0
        assert isinstance(bm.mape_pct, float) and bm.mape_pct > 0.0
        assert isinstance(bm.r2_score, float)
        assert bm.sample_count == eval_res.evaluation_hours


def test_xgboost_evaluation_and_improvements():
    """Verify real XGBoost model evaluation produces valid numeric metrics and structured comparisons."""
    eval_res = evaluate_chronological_demand_models(total_hours=504, seed=42)

    # Real XGBoost model metrics must be valid finite floats
    assert isinstance(eval_res.xgboost_model.mae, float) and eval_res.xgboost_model.mae > 0.0
    assert isinstance(eval_res.xgboost_model.rmse, float) and eval_res.xgboost_model.rmse > 0.0
    assert isinstance(eval_res.xgboost_model.mape_pct, float) and eval_res.xgboost_model.mape_pct > 0.0
    assert isinstance(eval_res.xgboost_model.r2_score, float)
    assert eval_res.xgboost_model.sample_count == eval_res.evaluation_hours

    # Improvements dictionary
    assert "vs_lag_1" in eval_res.improvements_pct
    assert "vs_lag_24" in eval_res.improvements_pct
    assert "vs_lag_168" in eval_res.improvements_pct

    for base_key in ["vs_lag_1", "vs_lag_24", "vs_lag_168"]:
        assert "mae_improvement_pct" in eval_res.improvements_pct[base_key]
        assert "rmse_improvement_pct" in eval_res.improvements_pct[base_key]
        assert isinstance(eval_res.improvements_pct[base_key]["mae_improvement_pct"], float)
        assert isinstance(eval_res.improvements_pct[base_key]["rmse_improvement_pct"], float)

    # Markdown table formatting
    md_table = eval_res.to_markdown_table()
    assert "| Model / Baseline |" in md_table
    assert "Real XGBoost Demand Model" in md_table
    assert "Previous Hour (Lag 1)" in md_table
    assert "Same Hour Prev Day (Lag 24)" in md_table
    assert "Same Hour Prev Week (Lag 168)" in md_table



def test_chronological_preservation_no_data_shuffling():
    """Verify evaluation strictly preserves chronological time-series ordering."""
    dates = pd.date_range("2026-08-01", periods=300, freq="h", tz="UTC")
    # Linear ramp to explicitly verify temporal lag alignment
    demands = [float(i + 10.0) for i in range(300)]
    df = pd.DataFrame({
        "timestamp": [d.isoformat() for d in dates],
        "hour": [d.hour for d in dates],
        "day_of_week": [d.weekday() for d in dates],
        "target_demand_mw": demands,
    })

    eval_res = evaluate_chronological_demand_models(df=df)

    # For a linear sequence with step +1.0 per hour:
    # Lag 1 error is exactly 1.0 everywhere
    assert np.isclose(eval_res.baseline_previous_hour.mae, 1.0, atol=1e-3)
    # Lag 24 error is exactly 24.0 everywhere
    assert np.isclose(eval_res.baseline_same_hour_prev_day.mae, 24.0, atol=1e-3)
    # Lag 168 error is exactly 168.0 everywhere
    assert np.isclose(eval_res.baseline_same_hour_prev_week.mae, 168.0, atol=1e-3)
