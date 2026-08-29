from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ForecastType(str, Enum):
    LOAD = "load"
    SOLAR = "solar"
    WIND = "wind"


class ForecastDataPoint(BaseModel):
    timestamp: str = Field(..., description="ISO timestamp for forecast point")
    value_mw: float = Field(..., description="Point forecast in MW")
    lower_bound_mw: Optional[float] = Field(None, description="P10 lower bound confidence interval in MW")
    upper_bound_mw: Optional[float] = Field(None, description="P90 upper bound confidence interval in MW")


class ForecastRequest(BaseModel):
    forecast_type: ForecastType = Field(
        default=ForecastType.LOAD,
        description="Forecast metric category: load, solar, wind",
        json_schema_extra={"example": "load"},
    )
    horizon_hours: int = Field(
        default=24,
        ge=1,
        le=168,
        description="Forecasting horizon in hours (1-168)",
        json_schema_extra={"example": 24},
    )
    region_id: Optional[str] = Field(None, description="Optional substation or grid region identifier")
    weather_factors: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional exogenous weather adjustments")


class ForecastResponse(BaseModel):
    forecast_type: ForecastType = Field(..., description="Validated forecast category")
    horizon_hours: int = Field(..., description="Horizon duration in hours")
    values: List[ForecastDataPoint] = Field(..., description="Time-series forecasted points")
    peak_mw: float = Field(..., description="Peak forecast value across the horizon in MW")
    min_mw: float = Field(..., description="Minimum forecast value across the horizon in MW")
    average_mw: float = Field(..., description="Mean forecasted output/demand in MW")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Forecast generation timestamp",
    )
