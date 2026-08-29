"""
PULSEiQ - Forecasting Module.
Contains machine learning load demand, solar, and wind generation forecasters (XGBoost, Scikit-Learn).
"""

from ai.forecasting.models import (
    ForecastResult,
    ForecastTarget,
    GridForecastSummary,
    TimeSeriesPoint,
)
from ai.forecasting.generators import (
    generate_synthetic_load_dataset,
    generate_synthetic_solar_dataset,
    generate_synthetic_weather,
    generate_synthetic_wind_dataset,
)
from ai.forecasting.forecaster import (
    DemandForecaster,
    GridForecaster,
    SolarForecaster,
    WindForecaster,
)

__all__ = [
    "ForecastTarget",
    "TimeSeriesPoint",
    "ForecastResult",
    "GridForecastSummary",
    "generate_synthetic_weather",
    "generate_synthetic_load_dataset",
    "generate_synthetic_solar_dataset",
    "generate_synthetic_wind_dataset",
    "DemandForecaster",
    "SolarForecaster",
    "WindForecaster",
    "GridForecaster",
]
