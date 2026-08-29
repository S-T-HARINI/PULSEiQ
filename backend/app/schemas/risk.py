from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AffectedComponent(BaseModel):
    id: str = Field(..., description="Component identifier")
    name: str = Field(..., description="Human readable component name")
    type: str = Field(..., description="Asset type: node or line")
    impact: str = Field(..., description="Impact nature: overloaded, tripped, isolated, voltage_drop")
    utilization_or_loading: Optional[float] = Field(None, description="Loading or utilization percentage")


class RiskAnalysisRequest(BaseModel):
    contingency_type: Optional[str] = Field(
        default="N-1",
        description="Contingency category: N-1, extreme_weather, solar_ramp, or custom",
        json_schema_extra={"example": "N-1"},
    )
    scenario_info: Optional[str] = Field(None, description="Contextual scenario description")
    failed_component_id: Optional[str] = Field(
        None,
        description="Forced component outage identifier",
        json_schema_extra={"example": "line-north-central-1"},
    )
    monte_carlo_iterations: int = Field(
        default=1000,
        ge=10,
        le=100000,
        description="Monte Carlo iteration count",
        json_schema_extra={"example": 1000},
    )
    grid_state_override: Optional[Dict[str, Any]] = Field(default=None, description="Optional custom grid state")


class RiskAnalysisResponse(BaseModel):
    risk_index: float = Field(..., description="Composite risk index from 0.0 (safe) to 1.0 (critical)", json_schema_extra={"example": 0.35})
    risk_level: RiskLevel = Field(..., description="Categorical risk classification: low, moderate, high, critical")
    affected_components: List[AffectedComponent] = Field(..., description="List of components at risk or degraded")
    affected_load_mw: float = Field(..., description="Total consumer load facing supply degradation in MW")
    critical_load_at_risk: bool = Field(..., description="Whether hospital or critical infrastructure load is threatened")
    critical_load_at_risk_mw: float = Field(default=0.0, description="Amount of critical tier-1 load under threat in MW")
    cascading_failure_indicators: Dict[str, Any] = Field(..., description="Metrics regarding potential cascading failure propagation")
    explanation: str = Field(..., description="Human-readable engineering explanation of risk drivers")
    summary: Dict[str, Any] = Field(..., description="Summary metrics including LOLP and EENS estimations")
    analyzed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Analysis timestamp",
    )
