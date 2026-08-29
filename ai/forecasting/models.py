"""
PULSEiQ - Forecasting Data Structures & Result Models.
Typed representations of time-series points, probabilistic confidence intervals,
forecast results, and aggregate grid load/generation forecast curves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ForecastTarget(str, Enum):
    """Target variable type for forecasting."""
    DEMAND = "demand"
    SOLAR = "solar"
    WIND = "wind"


@dataclass
class TimeSeriesPoint:
    """A single forecasted time point."""
    timestamp: str  # ISO 8601 string, e.g. "2026-08-29T12:00:00Z"
    hour_index: int
    value_mw: float
    confidence_lower: float  # e.g., 10th percentile
    confidence_upper: float  # e.g., 90th percentile

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "hour_index": self.hour_index,
            "value_mw": round(self.value_mw, 3),
            "confidence_lower": round(self.confidence_lower, 3),
            "confidence_upper": round(self.confidence_upper, 3),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TimeSeriesPoint:
        return cls(
            timestamp=str(data["timestamp"]),
            hour_index=int(data["hour_index"]),
            value_mw=float(data["value_mw"]),
            confidence_lower=float(data.get("confidence_lower", data["value_mw"])),
            confidence_upper=float(data.get("confidence_upper", data["value_mw"])),
        )


@dataclass
class ForecastResult:
    """Forecast result for a specific node or asset."""
    target_id: str
    target_name: str
    target_type: ForecastTarget
    horizon_hours: int
    points: List[TimeSeriesPoint] = field(default_factory=list)
    peak_mw: float = 0.0
    min_mw: float = 0.0
    average_mw: float = 0.0
    total_mwh: float = 0.0
    model_name: str = "XGBoostRegressor"
    metrics: Dict[str, float] = field(default_factory=dict)  # e.g. {"mae": 1.2, "rmse": 1.8}

    def __post_init__(self):
        if self.points and (self.peak_mw == 0.0 and self.total_mwh == 0.0):
            values = [p.value_mw for p in self.points]
            self.peak_mw = max(values)
            self.min_mw = min(values)
            self.average_mw = sum(values) / len(values)
            self.total_mwh = sum(values)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_name": self.target_name,
            "target_type": self.target_type.value,
            "horizon_hours": self.horizon_hours,
            "peak_mw": round(self.peak_mw, 3),
            "min_mw": round(self.min_mw, 3),
            "average_mw": round(self.average_mw, 3),
            "total_mwh": round(self.total_mwh, 3),
            "model_name": self.model_name,
            "metrics": dict(self.metrics),
            "points": [p.to_dict() for p in self.points],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ForecastResult:
        return cls(
            target_id=str(data["target_id"]),
            target_name=str(data["target_name"]),
            target_type=ForecastTarget(data["target_type"]),
            horizon_hours=int(data["horizon_hours"]),
            points=[TimeSeriesPoint.from_dict(p) for p in data.get("points", [])],
            peak_mw=float(data.get("peak_mw", 0.0)),
            min_mw=float(data.get("min_mw", 0.0)),
            average_mw=float(data.get("average_mw", 0.0)),
            total_mwh=float(data.get("total_mwh", 0.0)),
            model_name=str(data.get("model_name", "XGBoostRegressor")),
            metrics=dict(data.get("metrics", {})),
        )


@dataclass
class GridForecastSummary:
    """Aggregate system-wide multi-asset forecast summary."""
    horizon_hours: int
    timestamps: List[str]
    demand_forecasts: Dict[str, ForecastResult] = field(default_factory=dict)
    solar_forecasts: Dict[str, ForecastResult] = field(default_factory=dict)
    wind_forecasts: Dict[str, ForecastResult] = field(default_factory=dict)
    total_demand_curve: List[float] = field(default_factory=list)
    total_renewable_curve: List[float] = field(default_factory=list)
    net_load_curve: List[float] = field(default_factory=list)  # Demand - Renewable
    peak_net_load_mw: float = 0.0
    summary_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_hours": self.horizon_hours,
            "timestamps": list(self.timestamps),
            "demand_forecasts": {k: v.to_dict() for k, v in self.demand_forecasts.items()},
            "solar_forecasts": {k: v.to_dict() for k, v in self.solar_forecasts.items()},
            "wind_forecasts": {k: v.to_dict() for k, v in self.wind_forecasts.items()},
            "total_demand_curve": [round(x, 3) for x in self.total_demand_curve],
            "total_renewable_curve": [round(x, 3) for x in self.total_renewable_curve],
            "net_load_curve": [round(x, 3) for x in self.net_load_curve],
            "peak_net_load_mw": round(self.peak_net_load_mw, 3),
            "summary_metrics": dict(self.summary_metrics),
        }
