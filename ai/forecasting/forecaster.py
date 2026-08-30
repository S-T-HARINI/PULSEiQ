"""
PULSEiQ - Machine Learning Forecasters for Demand, Solar, and Wind Generation.
Implements modular forecasters leveraging XGBoost and Scikit-Learn with
probabilistic uncertainty bounds and a unified grid forecast orchestrator.
"""

from __future__ import annotations

import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from ai.forecasting.generators import (
    extract_forecasting_features,
    generate_synthetic_load_dataset,
    generate_synthetic_solar_dataset,
    generate_synthetic_weather,
    generate_synthetic_wind_dataset,
)
from ai.forecasting.models import (
    ForecastResult,
    ForecastTarget,
    GridForecastSummary,
    TimeSeriesPoint,
)
from ai.models.grid import ElectricityGrid, GridNode, NodeType


# Default artifact locations
DEFAULT_ARTIFACT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "artifacts")
DEFAULT_DEMAND_MODEL_PATH = os.path.join(DEFAULT_ARTIFACT_DIR, "demand_model.joblib")
DEFAULT_METADATA_PATH = os.path.join(DEFAULT_ARTIFACT_DIR, "model_metadata.json")


class DemandForecaster:
    """
    Load Demand Forecaster using pre-trained HistGradientBoostingRegressor on UCI Electricity Data
    with fallback to runtime XGBoost / Gradient Boosting.
    Predicts multi-step hourly electrical demand (MW) with upper and lower confidence intervals.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
        n_estimators: int = 100,
        learning_rate: float = 0.08,
        seed: int = 42,
        auto_load_artifact: bool = True,
    ):
        self.seed = seed
        self.is_trained_model = False
        self.model_loaded = False
        self.feature_columns: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.training_mae = 0.0
        self.training_rmse = 0.0
        self.training_mape = 0.0
        self.training_r2 = 0.0
        self.error_residual_std = 0.0
        self.mean_demand_mw = 216.72

        target_model_path = model_path or DEFAULT_DEMAND_MODEL_PATH
        target_metadata_path = metadata_path or DEFAULT_METADATA_PATH

        if auto_load_artifact and os.path.exists(target_model_path):
            try:
                self.model = joblib.load(target_model_path)
                if os.path.exists(target_metadata_path):
                    with open(target_metadata_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
                else:
                    self.metadata = {}

                self.feature_columns = self.metadata.get("feature_columns", [
                    "hour", "hour_sin", "hour_cos",
                    "day_of_week", "dow_sin", "dow_cos",
                    "day_of_month", "month", "month_sin", "month_cos",
                    "is_weekend",
                    "lag_1", "lag_2", "lag_3", "lag_24", "lag_48", "lag_168",
                    "rolling_mean_6", "rolling_mean_24", "rolling_std_24",
                    "rolling_min_24", "rolling_max_24", "daily_ratio"
                ])

                test_m = self.metadata.get("test_metrics", {})
                val_m = self.metadata.get("validation_metrics", {})
                self.training_mae = float(test_m.get("mae", val_m.get("mae", 4.5091)))
                self.training_rmse = float(test_m.get("rmse", val_m.get("rmse", 6.5816)))
                self.training_mape = float(test_m.get("mape_pct", val_m.get("mape_pct", 2.018)))
                self.training_r2 = float(test_m.get("r2", val_m.get("r2", 0.9943)))
                self.error_residual_std = float(self.metadata.get("error_residual_std", 5.6706))
                self.mean_demand_mw = float(self.metadata.get("mean_demand_mw", 216.72))

                self.model_name = "HistGradientBoostingRegressor-trained"
                self.is_fitted = True
                self.is_trained_model = True
                self.model_loaded = True
            except Exception:
                self.is_fitted = False
                self.is_trained_model = False
                self.model_loaded = False

        if not self.is_trained_model:
            self.model_name = "XGBoostRegressor" if HAS_XGBOOST else "GradientBoostingRegressor"
            if HAS_XGBOOST:
                self.model = xgb.XGBRegressor(
                    n_estimators=n_estimators,
                    learning_rate=learning_rate,
                    max_depth=5,
                    random_state=seed,
                    verbosity=0,
                )
            else:
                self.model = GradientBoostingRegressor(
                    n_estimators=n_estimators,
                    learning_rate=learning_rate,
                    max_depth=5,
                    random_state=seed,
                )
            self.is_fitted = False

    def fit(self, training_df: pd.DataFrame, target_col: str = "target_demand_mw") -> DemandForecaster:
        """Fit demand forecasting model on historical telemetry."""
        X, y = extract_forecasting_features(training_df, target_col=target_col)
        self.model.fit(X, y)
        self.is_fitted = True
        self.is_trained_model = False

        preds = self.model.predict(X)
        self.training_mae = float(mean_absolute_error(y, preds))
        self.training_rmse = float(np.sqrt(mean_squared_error(y, preds)))
        return self

    def predict(
        self,
        node: GridNode,
        horizon_hours: int = 24,
        weather_df: Optional[pd.DataFrame] = None,
        confidence_interval: float = 0.90,
        historical_series: Optional[List[float]] = None,
    ) -> ForecastResult:
        """
        Generate hourly demand forecast for a load node.
        Leverages the trained HistGradientBoostingRegressor with 23 engineered features
        and multi-step autoregressive rollout when available, or fallbacks to runtime baseline.
        """
        if weather_df is None:
            weather_df = generate_synthetic_weather(hours=horizon_hours, seed=self.seed)
        else:
            weather_df = weather_df.head(horizon_hours).copy()

        base_demand = float(node.operational.demand_mw if (node.operational and node.operational.demand_mw) else 20.0)
        base_demand = max(0.1, base_demand)

        # -------------------------------------------------------------
        # BRANCH 1: Saved Trained ML Model with 23 Feature Multi-Step Rollout
        # -------------------------------------------------------------
        if self.is_trained_model:
            # Parse timestamps
            timestamps_dt = []
            for ts in weather_df["timestamp"]:
                if isinstance(ts, datetime):
                    timestamps_dt.append(ts)
                else:
                    try:
                        timestamps_dt.append(datetime.fromisoformat(str(ts).replace("Z", "+00:00")))
                    except Exception:
                        timestamps_dt.append(datetime.now(timezone.utc))

            # Scale factor for node demand relative to trained aggregate load mean (~216.72 MW)
            scale_factor = base_demand / max(self.mean_demand_mw, 0.1)

            # Historical 168-hour context in node scale
            if historical_series is not None and len(historical_series) >= 168:
                history = [float(x) for x in historical_series[-168:]]
            else:
                start_dt = timestamps_dt[0] if timestamps_dt else datetime.now(timezone.utc)
                history = []
                for h_offset in range(168, 0, -1):
                    past_dt = start_dt - timedelta(hours=h_offset)
                    p_hour = past_dt.hour
                    p_dow = past_dt.weekday()
                    p_is_weekend = 1 if p_dow >= 5 else 0

                    if node.node_type == NodeType.LOAD_CRITICAL:
                        hourly_factor = 0.92 + 0.12 * (np.sin((p_hour - 8) * np.pi / 12.0) ** 2)
                        weekend_factor = 0.98 if p_is_weekend else 1.0
                    else:
                        morning_peak = np.exp(-((p_hour - 8) ** 2) / 8.0) * 0.25
                        evening_peak = np.exp(-((p_hour - 19) ** 2) / 10.0) * 0.40
                        hourly_factor = 0.60 + morning_peak + evening_peak
                        weekend_factor = 0.88 if p_is_weekend else 1.0

                    history.append(base_demand * hourly_factor * weekend_factor)

            # Sequential multi-step rollout without future lookahead
            predictions: List[float] = []
            for i, dt in enumerate(timestamps_dt):
                model_history = [val / scale_factor for val in history]

                hour = dt.hour
                dow = dt.weekday()
                dom = dt.day
                mon = dt.month
                is_wk = int(dow >= 5)

                lag_1 = model_history[-1]
                lag_2 = model_history[-2]
                lag_3 = model_history[-3]
                lag_24 = model_history[-24]
                lag_48 = model_history[-48]
                lag_168 = model_history[-168]

                past_6 = model_history[-6:]
                past_24 = model_history[-24:]
                r_mean_6 = float(np.mean(past_6))
                r_mean_24 = float(np.mean(past_24))
                r_std_24 = float(np.std(past_24, ddof=1)) if len(past_24) > 1 else 0.0
                r_min_24 = float(np.min(past_24))
                r_max_24 = float(np.max(past_24))
                daily_ratio = float(lag_1 / np.maximum(r_mean_24, 0.1))

                row_features = {
                    "hour": hour,
                    "hour_sin": float(np.sin(2 * np.pi * hour / 24.0)),
                    "hour_cos": float(np.cos(2 * np.pi * hour / 24.0)),
                    "day_of_week": dow,
                    "dow_sin": float(np.sin(2 * np.pi * dow / 7.0)),
                    "dow_cos": float(np.cos(2 * np.pi * dow / 7.0)),
                    "day_of_month": dom,
                    "month": mon,
                    "month_sin": float(np.sin(2 * np.pi * mon / 12.0)),
                    "month_cos": float(np.cos(2 * np.pi * mon / 12.0)),
                    "is_weekend": is_wk,
                    "lag_1": lag_1,
                    "lag_2": lag_2,
                    "lag_3": lag_3,
                    "lag_24": lag_24,
                    "lag_48": lag_48,
                    "lag_168": lag_168,
                    "rolling_mean_6": r_mean_6,
                    "rolling_mean_24": r_mean_24,
                    "rolling_std_24": r_std_24,
                    "rolling_min_24": r_min_24,
                    "rolling_max_24": r_max_24,
                    "daily_ratio": daily_ratio,
                }

                step_df = pd.DataFrame([row_features])[self.feature_columns]
                pred_model = float(self.model.predict(step_df)[0])
                pred_val = max(0.1, pred_model * scale_factor)

                predictions.append(pred_val)
                # Update history with new prediction for subsequent autoregressive steps
                history.append(pred_val)

            z_score = 1.645 if confidence_interval >= 0.90 else (1.282 if confidence_interval >= 0.80 else 1.0)
            uncertainty_std = max(self.error_residual_std * scale_factor, 0.03 * base_demand)

            points: List[TimeSeriesPoint] = []
            for i, (idx, row) in enumerate(weather_df.iterrows()):
                pred_val = float(predictions[i])
                lower = max(0.0, pred_val - z_score * uncertainty_std)
                upper = pred_val + z_score * uncertainty_std

                points.append(
                    TimeSeriesPoint(
                        timestamp=str(row["timestamp"]),
                        hour_index=i,
                        value_mw=round(pred_val, 3),
                        confidence_lower=round(lower, 3),
                        confidence_upper=round(upper, 3),
                    )
                )

            metrics = {
                "mae": round(self.training_mae, 4),
                "rmse": round(self.training_rmse, 4),
                "mape_pct": round(self.training_mape, 3),
                "r2": round(self.training_r2, 4),
            }

            return ForecastResult(
                target_id=node.id,
                target_name=node.name,
                target_type=ForecastTarget.DEMAND,
                horizon_hours=horizon_hours,
                points=points,
                model_name=self.model_name,
                metrics=metrics,
            )

        # -------------------------------------------------------------
        # BRANCH 2: Fallback Runtime Baseline Fitting
        # -------------------------------------------------------------
        if not self.is_fitted:
            hist_df = generate_synthetic_load_dataset(
                node_id=node.id,
                node_type=node.node_type,
                base_demand_mw=node.operational.demand_mw or 20.0,
                hours=336,  # 2 weeks history
                seed=self.seed,
            )
            self.fit(hist_df)

        X_future, _ = extract_forecasting_features(weather_df, target_col="none")
        predictions = self.model.predict(X_future)
        predictions = np.maximum(predictions, 0.1)  # Non-negative loads

        uncertainty_std = max(self.training_rmse, 0.03 * (node.operational.demand_mw or 10.0))
        z_score = 1.645 if confidence_interval >= 0.90 else 1.0

        points: List[TimeSeriesPoint] = []
        for i, (idx, row) in enumerate(weather_df.iterrows()):
            pred_val = float(predictions[i])
            lower = max(0.0, pred_val - z_score * uncertainty_std)
            upper = pred_val + z_score * uncertainty_std

            points.append(
                TimeSeriesPoint(
                    timestamp=str(row["timestamp"]),
                    hour_index=i,
                    value_mw=round(pred_val, 3),
                    confidence_lower=round(lower, 3),
                    confidence_upper=round(upper, 3),
                )
            )

        return ForecastResult(
            target_id=node.id,
            target_name=node.name,
            target_type=ForecastTarget.DEMAND,
            horizon_hours=horizon_hours,
            points=points,
            model_name=self.model_name,
            metrics={"mae": round(self.training_mae, 3), "rmse": round(self.training_rmse, 3)},
        )


class SolarForecaster:
    """
    Solar PV Generation Forecaster utilizing irradiance, temperature, and sun angle.
    """

    def __init__(self, n_estimators: int = 100, seed: int = 42):
        self.seed = seed
        self.model_name = "XGBoostSolarRegressor" if HAS_XGBOOST else "GradientBoostingSolarRegressor"
        if HAS_XGBOOST:
            self.model = xgb.XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=0.08,
                max_depth=4,
                random_state=seed,
                verbosity=0,
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                learning_rate=0.08,
                max_depth=4,
                random_state=seed,
            )
        self.is_fitted = False
        self.training_mae = 0.0
        self.training_rmse = 0.0

    def fit(self, training_df: pd.DataFrame, target_col: str = "target_generation_mw") -> SolarForecaster:
        """Fit solar forecasting model on historical solar records."""
        X, y = extract_forecasting_features(training_df, target_col=target_col)
        self.model.fit(X, y)
        self.is_fitted = True

        preds = self.model.predict(X)
        self.training_mae = float(mean_absolute_error(y, preds))
        self.training_rmse = float(np.sqrt(mean_squared_error(y, preds)))
        return self

    def predict(
        self,
        node: GridNode,
        horizon_hours: int = 24,
        weather_df: Optional[pd.DataFrame] = None,
    ) -> ForecastResult:
        """Generate solar generation forecast for solar farm asset."""
        capacity = node.operational.max_capacity_mw or 45.0
        if weather_df is None:
            weather_df = generate_synthetic_weather(hours=horizon_hours, seed=self.seed)
        else:
            weather_df = weather_df.head(horizon_hours).copy()

        if not self.is_fitted:
            hist_df = generate_synthetic_solar_dataset(
                node_id=node.id,
                capacity_mw=capacity,
                hours=336,
                seed=self.seed,
            )
            self.fit(hist_df)

        X_future, _ = extract_forecasting_features(weather_df, target_col="none")
        predictions = self.model.predict(X_future)

        # Zero night hours and bound to nameplate capacity
        points: List[TimeSeriesPoint] = []
        for i, (idx, row) in enumerate(weather_df.iterrows()):
            irr = row["solar_irradiance_wm2"]
            if irr <= 5.0:
                pred_val = 0.0
                lower = 0.0
                upper = 0.0
            else:
                pred_val = float(np.clip(predictions[i], 0.0, capacity))
                lower = float(max(0.0, pred_val * 0.88))
                upper = float(min(capacity, pred_val * 1.12))

            points.append(
                TimeSeriesPoint(
                    timestamp=row["timestamp"],
                    hour_index=i,
                    value_mw=round(pred_val, 3),
                    confidence_lower=round(lower, 3),
                    confidence_upper=round(upper, 3),
                )
            )

        return ForecastResult(
            target_id=node.id,
            target_name=node.name,
            target_type=ForecastTarget.SOLAR,
            horizon_hours=horizon_hours,
            points=points,
            model_name=self.model_name,
            metrics={"mae": round(self.training_mae, 3), "rmse": round(self.training_rmse, 3)},
        )


class WindForecaster:
    """
    Wind Generation Forecaster modeling turbine aerodynamic response to speed and gust profiles.
    """

    def __init__(self, n_estimators: int = 100, seed: int = 42):
        self.seed = seed
        self.model_name = "XGBoostWindRegressor" if HAS_XGBOOST else "GradientBoostingWindRegressor"
        if HAS_XGBOOST:
            self.model = xgb.XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=0.08,
                max_depth=4,
                random_state=seed,
                verbosity=0,
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=n_estimators,
                learning_rate=0.08,
                max_depth=4,
                random_state=seed,
            )
        self.is_fitted = False
        self.training_mae = 0.0
        self.training_rmse = 0.0

    def fit(self, training_df: pd.DataFrame, target_col: str = "target_generation_mw") -> WindForecaster:
        """Fit wind generation model on wind historical telemetry."""
        X, y = extract_forecasting_features(training_df, target_col=target_col)
        self.model.fit(X, y)
        self.is_fitted = True

        preds = self.model.predict(X)
        self.training_mae = float(mean_absolute_error(y, preds))
        self.training_rmse = float(np.sqrt(mean_squared_error(y, preds)))
        return self

    def predict(
        self,
        node: GridNode,
        horizon_hours: int = 24,
        weather_df: Optional[pd.DataFrame] = None,
    ) -> ForecastResult:
        """Generate wind generation forecast for wind turbine farm."""
        capacity = node.operational.max_capacity_mw or 50.0
        if weather_df is None:
            weather_df = generate_synthetic_weather(hours=horizon_hours, seed=self.seed)
        else:
            weather_df = weather_df.head(horizon_hours).copy()

        if not self.is_fitted:
            hist_df = generate_synthetic_wind_dataset(
                node_id=node.id,
                capacity_mw=capacity,
                hours=336,
                seed=self.seed,
            )
            self.fit(hist_df)

        X_future, _ = extract_forecasting_features(weather_df, target_col="none")
        predictions = self.model.predict(X_future)

        points: List[TimeSeriesPoint] = []
        for i, (idx, row) in enumerate(weather_df.iterrows()):
            v = row["wind_speed_mps"]
            if v < 3.0 or v >= 25.0:
                pred_val = 0.0
                lower = 0.0
                upper = 0.0
            else:
                pred_val = float(np.clip(predictions[i], 0.0, capacity))
                lower = float(max(0.0, pred_val * 0.85))
                upper = float(min(capacity, pred_val * 1.15))

            points.append(
                TimeSeriesPoint(
                    timestamp=row["timestamp"],
                    hour_index=i,
                    value_mw=round(pred_val, 3),
                    confidence_lower=round(lower, 3),
                    confidence_upper=round(upper, 3),
                )
            )

        return ForecastResult(
            target_id=node.id,
            target_name=node.name,
            target_type=ForecastTarget.WIND,
            horizon_hours=horizon_hours,
            points=points,
            model_name=self.model_name,
            metrics={"mae": round(self.training_mae, 3), "rmse": round(self.training_rmse, 3)},
        )


class GridForecaster:
    """
    Unified Grid Forecaster orchestrating multi-asset forecasts across an ElectricityGrid.
    """

    def __init__(self, seed: int = 42):
        self.demand_forecaster = DemandForecaster(seed=seed)
        self.solar_forecaster = SolarForecaster(seed=seed)
        self.wind_forecaster = WindForecaster(seed=seed)
        self.seed = seed

    def forecast_grid(
        self,
        grid: ElectricityGrid,
        horizon_hours: int = 24,
        weather_df: Optional[pd.DataFrame] = None,
    ) -> GridForecastSummary:
        """
        Executes comprehensive 24-hour / multi-period forecasts across all loads and renewables.
        """
        if weather_df is None:
            weather_df = generate_synthetic_weather(hours=horizon_hours, seed=self.seed)

        timestamps = [row["timestamp"] for _, row in weather_df.iterrows()]

        demand_forecasts: Dict[str, ForecastResult] = {}
        solar_forecasts: Dict[str, ForecastResult] = {}
        wind_forecasts: Dict[str, ForecastResult] = {}

        # 1. Forecast all load nodes
        for node in grid.nodes.values():
            if node.node_type in (NodeType.LOAD_NORMAL, NodeType.LOAD_CRITICAL):
                res = self.demand_forecaster.predict(node, horizon_hours=horizon_hours, weather_df=weather_df)
                demand_forecasts[node.id] = res

        # 2. Forecast all solar nodes
        for node in grid.nodes.values():
            if node.node_type == NodeType.SOLAR:
                res = self.solar_forecaster.predict(node, horizon_hours=horizon_hours, weather_df=weather_df)
                solar_forecasts[node.id] = res

        # 3. Forecast all wind nodes
        for node in grid.nodes.values():
            if node.node_type == NodeType.WIND:
                res = self.wind_forecaster.predict(node, horizon_hours=horizon_hours, weather_df=weather_df)
                wind_forecasts[node.id] = res

        # 4. Aggregate system curves
        total_demand_curve = [0.0] * horizon_hours
        total_renewable_curve = [0.0] * horizon_hours

        for d_res in demand_forecasts.values():
            for pt in d_res.points:
                total_demand_curve[pt.hour_index] += pt.value_mw

        for s_res in solar_forecasts.values():
            for pt in s_res.points:
                total_renewable_curve[pt.hour_index] += pt.value_mw

        for w_res in wind_forecasts.values():
            for pt in w_res.points:
                total_renewable_curve[pt.hour_index] += pt.value_mw

        net_load_curve = [
            max(0.0, total_demand_curve[i] - total_renewable_curve[i])
            for i in range(horizon_hours)
        ]
        peak_net_load = max(net_load_curve) if net_load_curve else 0.0

        return GridForecastSummary(
            horizon_hours=horizon_hours,
            timestamps=timestamps,
            demand_forecasts=demand_forecasts,
            solar_forecasts=solar_forecasts,
            wind_forecasts=wind_forecasts,
            total_demand_curve=total_demand_curve,
            total_renewable_curve=total_renewable_curve,
            net_load_curve=net_load_curve,
            peak_net_load_mw=peak_net_load,
            summary_metrics={
                "total_demand_mwh": round(sum(total_demand_curve), 2),
                "total_renewable_mwh": round(sum(total_renewable_curve), 2),
                "peak_gross_demand_mw": round(max(total_demand_curve) if total_demand_curve else 0.0, 2),
                "renewable_penetration_pct": round(
                    (sum(total_renewable_curve) / max(sum(total_demand_curve), 1.0)) * 100.0, 2
                ),
            },
        )
