"""
PULSEiQ - Machine Learning Forecasters for Demand, Solar, and Wind Generation.
Implements modular forecasters leveraging XGBoost and Scikit-Learn with
probabilistic uncertainty bounds and a unified grid forecast orchestrator.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

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


class DemandForecaster:
    """
    Load Demand Forecaster using XGBoost / Gradient Boosting.
    Predicts multi-step hourly electrical demand (MW) with upper and lower confidence intervals.
    """

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.08, seed: int = 42):
        self.seed = seed
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
        self.training_mae = 0.0
        self.training_rmse = 0.0

    def fit(self, training_df: pd.DataFrame, target_col: str = "target_demand_mw") -> DemandForecaster:
        """Fit demand forecasting model on historical telemetry."""
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
        confidence_interval: float = 0.90,
    ) -> ForecastResult:
        """
        Generate hourly demand forecast for a load node.
        """
        if weather_df is None:
            weather_df = generate_synthetic_weather(hours=horizon_hours, seed=self.seed)
        else:
            weather_df = weather_df.head(horizon_hours).copy()

        # If model is not yet fitted, auto-fit on synthetic historical baseline
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

        # Uncertainty error bounds
        uncertainty_std = max(self.training_rmse, 0.03 * (node.operational.demand_mw or 10.0))
        z_score = 1.645 if confidence_interval >= 0.90 else 1.0

        points: List[TimeSeriesPoint] = []
        for i, (idx, row) in enumerate(weather_df.iterrows()):
            pred_val = float(predictions[i])
            lower = max(0.0, pred_val - z_score * uncertainty_std)
            upper = pred_val + z_score * uncertainty_std

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
