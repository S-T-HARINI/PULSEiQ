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


class CriticalLoadImpact(BaseModel):
    critical_load_at_risk: bool = Field(..., description="Whether hospital or tier-1 critical loads are threatened")
    critical_load_at_risk_mw: float = Field(default=0.0, description="Amount of critical tier-1 load under threat in MW")
    affected_critical_facilities: List[str] = Field(default_factory=list, description="Names of threatened critical facilities")


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
    grid_state: Optional[Dict[str, Any]] = Field(default=None, description="Current or simulated grid state")
    simulation_results: Optional[Dict[str, Any]] = Field(default=None, description="Output from prior simulation run")


class RiskAnalysisResponse(BaseModel):
    risk_index: float = Field(..., description="Composite risk index from 0.0 (safe) to 1.0 (critical)", json_schema_extra={"example": 0.35})
    risk_level: RiskLevel = Field(..., description="Categorical risk classification: low, moderate, high, critical")
    vulnerable_components: List[AffectedComponent] = Field(
        default_factory=list,
        description="List of vulnerable grid assets identified by graph and risk models",
    )
    affected_components: List[AffectedComponent] = Field(
        default_factory=list,
        description="Alias list of affected components",
    )
    critical_load_impact: CriticalLoadImpact = Field(
        ...,
        description="Structured assessment of threats to critical infrastructure",
    )
    contingency_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detailed contingency screening outcomes",
    )
    n1_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Deterministic N-1 line trip and generator outage screening metrics",
    )
    cascading_failure_indicators: Dict[str, Any] = Field(
        ...,
        description="Metrics regarding potential cascading failure propagation from NetworkX graph models",
    )
    model_source: str = Field(
        default="ai_module",
        description="Risk engine source: ai_module or service_fallback",
        json_schema_extra={"example": "ai_module"},
    )
    explanation: str = Field(..., description="Human-readable engineering explanation of risk drivers")
    summary: Dict[str, Any] = Field(..., description="Summary metrics including LOLP and EENS estimations")
    analyzed_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Analysis timestamp",
    )
