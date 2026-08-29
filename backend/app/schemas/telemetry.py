from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class GridOperationalStatus(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"
    CONTINGENCY = "CONTINGENCY"


class GridTelemetryMessage(BaseModel):
    message_type: str = Field(
        default="grid_telemetry",
        description="Type identifier for the WebSocket message frame",
        json_schema_extra={"example": "grid_telemetry"},
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp of telemetry measurement",
    )
    grid_status: GridOperationalStatus = Field(
        default=GridOperationalStatus.NORMAL,
        description="High-level operational status of the grid system",
        json_schema_extra={"example": "NORMAL"},
    )
    total_generation: float = Field(
        ...,
        description="Total active power generation across all online units in MW",
        json_schema_extra={"example": 475.2},
    )
    total_demand: float = Field(
        ...,
        description="Total active consumer load demand in MW",
        json_schema_extra={"example": 461.5},
    )
    renewable_generation_percent: float = Field(
        ...,
        description="Percentage of total generation supplied by solar and wind",
        ge=0.0,
        le=100.0,
        json_schema_extra={"example": 49.5},
    )
    battery_soc: float = Field(
        ...,
        description="Aggregate Battery Energy Storage System State of Charge (0-100%)",
        ge=0.0,
        le=100.0,
        json_schema_extra={"example": 78.5},
    )
    grid_risk_index: float = Field(
        ...,
        description="Real-time operational risk index (0.0=safe, 1.0=critical)",
        ge=0.0,
        le=1.0,
        json_schema_extra={"example": 0.14},
    )
    frequency_hz: float = Field(
        default=50.00,
        description="Simulated grid frequency in Hz",
        json_schema_extra={"example": 50.02},
    )
    line_utilization_avg: float = Field(
        default=56.4,
        description="Average thermal transmission line loading percentage",
        json_schema_extra={"example": 56.4},
    )
    affected_components: List[str] = Field(
        default_factory=list,
        description="List of component IDs currently flagged with warnings or outages",
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional asset-level telemetry snapshots and metadata",
    )


class ClientControlMessage(BaseModel):
    action: Optional[str] = Field(None, description="Control action requested by client: ping, subscribe, reset")
    channel: Optional[str] = Field(None, description="Requested telemetry channel")
