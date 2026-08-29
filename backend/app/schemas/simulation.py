from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SimulationRunRequest(BaseModel):
    scenario_id: Optional[str] = Field(None, description="Scenario ID or reference", json_schema_extra={"example": "scen_heatwave_01"})
    duration_hours: int = Field(24, description="Simulation duration in hours", ge=1, le=168, json_schema_extra={"example": 24})
    time_step_minutes: int = Field(60, description="Simulation time-step resolution in minutes", ge=1, le=60, json_schema_extra={"example": 60})
    demand_mw: Optional[float] = Field(None, description="Total active demand override in MW")
    generation_mw: Optional[float] = Field(None, description="Total generation dispatch override in MW")
    renewable_generation_mw: Optional[float] = Field(None, description="Renewable generation override in MW")
    battery_state: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Battery storage state parameters")
    load_growth_factor: Optional[float] = Field(1.0, description="Load scaling multiplier", ge=0.1, le=3.0, json_schema_extra={"example": 1.0})
    contingency_event: Optional[str] = Field(None, description="Forced contingency line/asset ID", json_schema_extra={"example": "line-north-central-1"})
    grid_state: Optional[Dict[str, Any]] = Field(default=None, description="Custom grid topology override")
    simulation_parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom numerical solver parameters")


# Aliases for backward compatibility
SimulationRequest = SimulationRunRequest


class SimulationRunResponse(BaseModel):
    simulation_status: str = Field(default="completed", description="Status of the simulation run", json_schema_extra={"example": "completed"})
    total_generation_mw: float = Field(..., description="Simulated total generation in MW", json_schema_extra={"example": 475.0})
    total_demand_mw: float = Field(..., description="Simulated total demand in MW", json_schema_extra={"example": 460.0})
    renewable_generation_mw: float = Field(..., description="Simulated renewable power generation in MW", json_schema_extra={"example": 235.0})
    line_utilization_avg: float = Field(..., description="Average transmission line loading percentage", json_schema_extra={"example": 56.4})
    line_loading: Dict[str, float] = Field(default_factory=dict, description="Per-transmission-line thermal loading percentage")
    frequency_hz: float = Field(default=50.00, description="Simulated grid system frequency in Hz", json_schema_extra={"example": 50.02})
    voltage_indicators: Dict[str, float] = Field(
        default_factory=lambda: {"min_voltage_pu": 0.982, "max_voltage_pu": 1.025, "avg_voltage_pu": 1.002},
        description="Per-unit (p.u.) bus voltage indicators",
    )
    simulation_warnings: List[str] = Field(default_factory=list, description="Simulation warnings and thermal/voltage constraint alerts")
    affected_components: List[str] = Field(default_factory=list, description="List of components experiencing operational deviations")
    risk_index: float = Field(..., description="Composite grid operational risk index (0.0 to 1.0)", json_schema_extra={"example": 0.14})
    resulting_grid_state: Optional[Dict[str, Any]] = Field(None, description="Updated grid topology and telemetry post-simulation")
    model_source: str = Field(default="ai_module", description="Engine used: ai_module or service_fallback", json_schema_extra={"example": "ai_module"})
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp of simulation completion",
    )
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional simulation diagnostics and telemetry")


# Aliases for backward compatibility
SimulationResponse = SimulationRunResponse
