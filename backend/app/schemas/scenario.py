from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ScenarioType(str, Enum):
    EXTREME_HEATWAVE = "extreme_heatwave"
    SOLAR_RAMP_DOWN = "solar_ramp_down"
    N1_LINE_TRIP = "n1_line_trip"
    WIND_STORM_CUTOFF = "wind_storm_cutoff"
    WIND_STORM = "wind_storm"


class ScenarioWhatIfRequest(BaseModel):
    scenario_type: ScenarioType = Field(
        ...,
        description="Scenario type: extreme_heatwave, solar_ramp_down, n1_line_trip, wind_storm_cutoff",
        json_schema_extra={"example": "extreme_heatwave"},
    )
    name: Optional[str] = Field(None, description="Display name for the what-if study", json_schema_extra={"example": "Summer Extreme Heatwave"})
    description: Optional[str] = Field(None, description="Detailed description of test conditions")
    demand_multiplier: float = Field(
        default=1.0,
        ge=0.1,
        le=5.0,
        description="Load demand multiplier (e.g. 1.25 for +25% load surge)",
        json_schema_extra={"example": 1.25},
    )
    solar_multiplier: float = Field(
        default=1.0,
        ge=0.0,
        le=3.0,
        description="Solar capacity factor multiplier (e.g. 0.3 for sudden cloud cover / ramp-down)",
        json_schema_extra={"example": 0.3},
    )
    wind_multiplier: float = Field(
        default=1.0,
        ge=0.0,
        le=3.0,
        description="Wind generation multiplier (e.g. 0.0 for high wind speed cut-off)",
        json_schema_extra={"example": 0.0},
    )
    battery_available: bool = Field(
        default=True,
        description="Whether battery storage is available to cushion fluctuations",
        json_schema_extra={"example": True},
    )
    failed_component_id: Optional[str] = Field(
        default=None,
        description="Component forced into outage for N-1 contingency analysis",
        json_schema_extra={"example": "line-north-central-1"},
    )
    current_grid_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional baseline grid state override",
    )


# Aliases for backward compatibility
ScenarioRequest = ScenarioWhatIfRequest


class ScenarioWhatIfResponse(BaseModel):
    scenario_id: str = Field(..., description="Unique scenario run identifier", json_schema_extra={"example": "scen_whatif_88a1b2"})
    scenario_type: ScenarioType = Field(..., description="Executed scenario category")
    scenario_name: str = Field(..., description="Scenario display name")
    name: str = Field(..., description="Alias for scenario_name")
    status: str = Field(default="completed", description="Execution status")
    changed_demand_mw: float = Field(..., description="Estimated total demand under scenario in MW")
    demand_mw: float = Field(..., description="Alias for changed_demand_mw")
    changed_generation_mw: float = Field(..., description="Estimated total generation under scenario in MW")
    generation_mw: float = Field(..., description="Alias for changed_generation_mw")
    renewable_share_percent: float = Field(..., description="Estimated renewable generation percentage (0-100%)")
    resulting_risk_index: float = Field(..., description="Calculated operational risk index (0.0 to 1.0)")
    risk_index: float = Field(..., description="Alias for resulting_risk_index")
    critical_load_reliability_percent: float = Field(..., description="Estimated critical load supply reliability percentage (0-100%)")
    critical_load_impact: Dict[str, Any] = Field(
        default_factory=dict,
        description="Assessment of critical loads (e.g. hospitals) under stress",
    )
    affected_components: List[str] = Field(..., description="List of component IDs experiencing stress or outage")
    recommended_response: List[str] = Field(
        default_factory=list,
        description="Recommended operational mitigation actions",
    )
    applied_parameters: Dict[str, Any] = Field(..., description="Multipliers and parameters applied in simulation")
    model_source: str = Field(default="ai_module", description="Engine used: ai_module or service_fallback")
    summary: Dict[str, Any] = Field(..., description="Structured scenario impact summary")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Scenario timestamp",
    )


# Aliases for backward compatibility
ScenarioResponse = ScenarioWhatIfResponse
