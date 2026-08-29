from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ForecastType(str, Enum):
    LOAD = "load"
    SOLAR = "solar"
    WIND = "wind"


class ForecastDataPoint(BaseModel):
    timestamp: str = Field(..., description="ISO timestamp for forecast interval")
    predicted_demand_mw: Optional[float] = Field(None, description="Predicted active load demand in MW")
    predicted_renewable_mw: Optional[float] = Field(None, description="Predicted renewable generation in MW")
    value_mw: float = Field(..., description="Primary forecast value in MW")
    lower_bound_mw: Optional[float] = Field(None, description="P10 confidence interval lower limit in MW")
    upper_bound_mw: Optional[float] = Field(None, description="P90 confidence interval upper limit in MW")


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
    historical_demand_mw: Optional[List[float]] = Field(
        default=None,
        description="Optional historical load readings for autoregressive / ML models",
    )
    weather_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Exogenous weather parameters: temperature_c, irradiance_w_m2, wind_speed_mps",
    )
    renewable_generation_info: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Installed renewable capacities and operational curtailment constraints",
    )
    region_id: Optional[str] = Field(None, description="Target substation or grid region identifier")


class ForecastResponse(BaseModel):
    forecast_type: ForecastType = Field(..., description="Validated forecast category")
    horizon_hours: int = Field(..., description="Horizon duration in hours")
    values: List[ForecastDataPoint] = Field(..., description="Time-series forecasted data points")
    peak_mw: float = Field(..., description="Peak forecasted value across the horizon in MW")
    min_mw: float = Field(..., description="Minimum forecasted value across the horizon in MW")
    average_mw: float = Field(..., description="Mean forecasted output/demand in MW")
    confidence_score: float = Field(
        default=0.92,
        description="Model prediction confidence score (0.0 to 1.0)",
        json_schema_extra={"example": 0.92},
    )
    model_source: str = Field(
        default="ai_module",
        description="Forecasting engine source: ai_module or service_fallback",
        json_schema_extra={"example": "ai_module"},
    )
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Forecast generation timestamp",
    )
