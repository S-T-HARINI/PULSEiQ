"""
PULSEiQ - Forecasting Model Evaluation & Baseline Benchmarking Module.
Provides chronological, non-shuffled time-series evaluation comparing the real trained
XGBoost demand forecasting model against standard heuristic baselines:
1. Previous-Hour Demand (Lag 1 / Persistence)
2. Same-Hour Previous-Day Demand (Lag 24 / Diurnal Seasonal Naive)
3. Same-Hour Previous-Week Demand (Lag 168 / Weekly Seasonal Naive)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from ai.forecasting.forecaster import (
    DEFAULT_MODEL_PATH,
    REAL_MODEL_FEATURE_NAMES,
    DemandForecaster,
    load_trained_demand_model,
)
from ai.forecasting.generators import generate_synthetic_load_dataset
from ai.models.grid import NodeType


@dataclass
class ModelEvaluationMetrics:
    """Evaluation metrics for a single model or baseline."""
    model_name: str
    mae: float
    rmse: float
    mape_pct: float
    r2_score: float
    sample_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ForecastingEvaluationResult:
    """Comprehensive benchmark comparison across baselines and the trained XGBoost model."""
    baseline_previous_hour: ModelEvaluationMetrics
    baseline_same_hour_prev_day: ModelEvaluationMetrics
    baseline_same_hour_prev_week: ModelEvaluationMetrics
    xgboost_model: ModelEvaluationMetrics
    evaluation_hours: int
    start_timestamp: Optional[str]
    end_timestamp: Optional[str]
    improvements_pct: Dict[str, Dict[str, float]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_previous_hour": self.baseline_previous_hour.to_dict(),
            "baseline_same_hour_prev_day": self.baseline_same_hour_prev_day.to_dict(),
            "baseline_same_hour_prev_week": self.baseline_same_hour_prev_week.to_dict(),
            "xgboost_model": self.xgboost_model.to_dict(),
            "evaluation_hours": self.evaluation_hours,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "improvements_pct": self.improvements_pct,
        }

    def to_markdown_table(self) -> str:
        """Format the benchmark results as a clean Markdown table for documentation & READMEs."""
        lines = [
            "| Model / Baseline | MAE (MW) | RMSE (MW) | MAPE (%) | R² Score | MAE vs Base | RMSE vs Base |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
            f"| **Previous Hour (Lag 1)** | {self.baseline_previous_hour.mae:.3f} | {self.baseline_previous_hour.rmse:.3f} | {self.baseline_previous_hour.mape_pct:.2f}% | {self.baseline_previous_hour.r2_score:.3f} | - | - |",
            f"| **Same Hour Prev Day (Lag 24)** | {self.baseline_same_hour_prev_day.mae:.3f} | {self.baseline_same_hour_prev_day.rmse:.3f} | {self.baseline_same_hour_prev_day.mape_pct:.2f}% | {self.baseline_same_hour_prev_day.r2_score:.3f} | - | - |",
            f"| **Same Hour Prev Week (Lag 168)** | {self.baseline_same_hour_prev_week.mae:.3f} | {self.baseline_same_hour_prev_week.rmse:.3f} | {self.baseline_same_hour_prev_week.mape_pct:.2f}% | {self.baseline_same_hour_prev_week.r2_score:.3f} | - | - |",
            f"| **Real XGBoost Demand Model** | **{self.xgboost_model.mae:.3f}** | **{self.xgboost_model.rmse:.3f}** | **{self.xgboost_model.mape_pct:.2f}%** | **{self.xgboost_model.r2_score:.3f}** | **+{self.improvements_pct['vs_lag_1']['mae_improvement_pct']:.1f}%** | **+{self.improvements_pct['vs_lag_1']['rmse_improvement_pct']:.1f}%** |",
        ]
        return "\n".join(lines)


def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
) -> ModelEvaluationMetrics:
    """
    Computes standard regression metrics (MAE, RMSE, MAPE, R2) between actual and predicted values.
    """
    y_true_arr = np.asarray(y_true, dtype=float)
    y_pred_arr = np.asarray(y_pred, dtype=float)

    n = len(y_true_arr)
    if n == 0:
        return ModelEvaluationMetrics(model_name=model_name, mae=0.0, rmse=0.0, mape_pct=0.0, r2_score=0.0, sample_count=0)

    errors = y_true_arr - y_pred_arr
    mae = float(np.mean(np.abs(errors)))
    rmse = float(np.sqrt(np.mean(errors ** 2)))

    # Prevent division by zero in MAPE
    denom = np.maximum(np.abs(y_true_arr), 1e-3)
    mape_pct = float(np.mean(np.abs(errors) / denom) * 100.0)

    # R-squared
    ss_tot = np.sum((y_true_arr - np.mean(y_true_arr)) ** 2)
    ss_res = np.sum(errors ** 2)
    r2_score = float(1.0 - (ss_res / ss_tot)) if ss_tot > 1e-6 else 0.0

    return ModelEvaluationMetrics(
        model_name=model_name,
        mae=round(mae, 4),
        rmse=round(rmse, 4),
        mape_pct=round(mape_pct, 2),
        r2_score=round(r2_score, 4),
        sample_count=n,
    )


def evaluate_chronological_demand_models(
    df: Optional[pd.DataFrame] = None,
    target_col: str = "target_demand_mw",
    total_hours: int = 504,  # 3 weeks total: 1 week history buffer (168h) + 2 weeks eval (336h)
    seed: int = 42,
    forecaster: Optional[DemandForecaster] = None,
) -> ForecastingEvaluationResult:
    """
    Executes strict chronological evaluation across:
    1. Previous-Hour Demand (Lag 1)
    2. Same-Hour Previous-Day Demand (Lag 24)
    3. Same-Hour Previous-Week Demand (Lag 168)
    4. Real Trained XGBoost Model

    Evaluation is performed strictly in chronological sequence with NO data shuffling.
    All models and baselines are tested on the exact same evaluation window.
    """
    if df is None:
        # Generate standard chronological load evaluation dataset
        df = generate_synthetic_load_dataset(
            node_id="eval_grid_load_node",
            node_type=NodeType.LOAD_NORMAL,
            base_demand_mw=50.0,
            hours=total_hours,
            seed=seed,
        )

    # Sort strictly by timestamp or index to enforce chronological order
    if "timestamp" in df.columns:
        df = df.sort_values(by="timestamp").reset_index(drop=True)
    else:
        df = df.reset_index(drop=True)

    series = df[target_col].to_numpy(dtype=float)
    total_len = len(series)

    # Minimum 168 hours history buffer needed for Lag 168
    eval_start_idx = 168
    if total_len <= eval_start_idx:
        raise ValueError(
            f"Dataset length ({total_len}) must be greater than 168 hours to evaluate weekly seasonal baseline."
        )

    eval_indices = range(eval_start_idx, total_len)
    eval_hours = len(eval_indices)

    y_true: List[float] = []
    y_pred_lag1: List[float] = []
    y_pred_lag24: List[float] = []
    y_pred_lag168: List[float] = []
    xgb_features: List[Dict[str, Any]] = []

    for t in eval_indices:
        actual_val = series[t]
        y_true.append(actual_val)

        # Baseline 1: Previous-hour demand (t - 1)
        y_pred_lag1.append(series[t - 1])

        # Baseline 2: Same-hour previous-day demand (t - 24)
        y_pred_lag24.append(series[t - 24])

        # Baseline 3: Same-hour previous-week demand (t - 168)
        y_pred_lag168.append(series[t - 168])

        # Extract real XGBoost features
        row = df.iloc[t]
        ts = row.get("timestamp")
        dt = pd.to_datetime(ts) if ts is not None else pd.Timestamp("2026-08-08 00:00:00") + pd.Timedelta(hours=t)

        hour = int(row["hour"]) if "hour" in row else int(dt.hour)
        day_of_week = int(row["day_of_week"]) if "day_of_week" in row else int(dt.weekday())
        month = int(dt.month) if hasattr(dt, "month") else 8

        xgb_features.append({
            "hour": hour,
            "day_of_week": day_of_week,
            "month": month,
            "lag_1": float(series[t - 1]),
            "lag_24": float(series[t - 24]),
            "lag_168": float(series[t - 168]),
        })

    # Predict using Real XGBoost Model
    if forecaster is None:
        forecaster = DemandForecaster(seed=seed)

    X_eval = pd.DataFrame(xgb_features)[REAL_MODEL_FEATURE_NAMES]

    if forecaster.using_real_model and forecaster.trained_model is not None:
        raw_xgb_preds = forecaster.trained_model.predict(X_eval)
        model_name = "RealTrainedXGBoost"
    else:
        # Fallback if trained model is missing
        if not forecaster.is_fitted:
            forecaster.fit(df.iloc[:eval_start_idx])
        raw_xgb_preds = forecaster.model.predict(X_eval)
        model_name = "SyntheticFittedForecaster"

    y_pred_xgb = [float(max(0.1, p)) for p in raw_xgb_preds]

    # Convert to numpy arrays
    y_true_arr = np.array(y_true)
    y_pred_lag1_arr = np.array(y_pred_lag1)
    y_pred_lag24_arr = np.array(y_pred_lag24)
    y_pred_lag168_arr = np.array(y_pred_lag168)
    y_pred_xgb_arr = np.array(y_pred_xgb)

    # Compute metrics for each model
    metrics_lag1 = calculate_metrics(y_true_arr, y_pred_lag1_arr, "Baseline: Previous Hour (Lag 1)")
    metrics_lag24 = calculate_metrics(y_true_arr, y_pred_lag24_arr, "Baseline: Same Hour Prev Day (Lag 24)")
    metrics_lag168 = calculate_metrics(y_true_arr, y_pred_lag168_arr, "Baseline: Same Hour Prev Week (Lag 168)")
    metrics_xgb = calculate_metrics(y_true_arr, y_pred_xgb_arr, f"Model: {model_name}")

    # Calculate improvements of XGBoost vs baselines
    improvements: Dict[str, Dict[str, float]] = {
        "vs_lag_1": {
            "mae_improvement_pct": round(((metrics_lag1.mae - metrics_xgb.mae) / max(metrics_lag1.mae, 1e-6)) * 100.0, 2),
            "rmse_improvement_pct": round(((metrics_lag1.rmse - metrics_xgb.rmse) / max(metrics_lag1.rmse, 1e-6)) * 100.0, 2),
        },
        "vs_lag_24": {
            "mae_improvement_pct": round(((metrics_lag24.mae - metrics_xgb.mae) / max(metrics_lag24.mae, 1e-6)) * 100.0, 2),
            "rmse_improvement_pct": round(((metrics_lag24.rmse - metrics_xgb.rmse) / max(metrics_lag24.rmse, 1e-6)) * 100.0, 2),
        },
        "vs_lag_168": {
            "mae_improvement_pct": round(((metrics_lag168.mae - metrics_xgb.mae) / max(metrics_lag168.mae, 1e-6)) * 100.0, 2),
            "rmse_improvement_pct": round(((metrics_lag168.rmse - metrics_xgb.rmse) / max(metrics_lag168.rmse, 1e-6)) * 100.0, 2),
        },
    }

    start_ts = str(df.iloc[eval_start_idx].get("timestamp")) if "timestamp" in df.columns else None
    end_ts = str(df.iloc[-1].get("timestamp")) if "timestamp" in df.columns else None

    return ForecastingEvaluationResult(
        baseline_previous_hour=metrics_lag1,
        baseline_same_hour_prev_day=metrics_lag24,
        baseline_same_hour_prev_week=metrics_lag168,
        xgboost_model=metrics_xgb,
        evaluation_hours=eval_hours,
        start_timestamp=start_ts,
        end_timestamp=end_ts,
        improvements_pct=improvements,
    )
