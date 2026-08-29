from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class OptimizationObjective(str, Enum):
    COST_MINIMIZATION = "cost_minimization"
    EMISSION_REDUCTION = "emission_reduction"
    RELIABILITY_MAXIMIZATION = "reliability_maximization"


class GeneratorDispatch(BaseModel):
    generator_id: str = Field(..., description="Generator identifier")
    generator_name: str = Field(..., description="Generator name")
    type: str = Field(..., description="Generation technology")
    dispatched_mw: float = Field(..., description="Optimal scheduled dispatch in MW")
    capacity_mw: float = Field(..., description="Maximum rated capacity in MW")
    marginal_cost_per_mwh: float = Field(..., description="Marginal production cost in $/MWh")


class OptimizationRunRequest(BaseModel):
    objective: OptimizationObjective = Field(
        default=OptimizationObjective.COST_MINIMIZATION,
        description="Target optimization objective",
        json_schema_extra={"example": "cost_minimization"},
    )
    demand_mw: Optional[float] = Field(None, description="Total active demand target in MW (defaults to grid total if None)")
    available_generation_mw: Optional[float] = Field(None, description="Total available generation capacity in MW")
    renewable_generation_mw: Optional[float] = Field(None, description="Available renewable supply in MW")
    current_grid_state: Optional[Dict[str, Any]] = Field(default=None, description="Current or simulated grid telemetry")
    battery_availability: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"soc_percent": 78.5, "capacity_mw": 80.0, "allow_discharge": True},
        description="Battery storage parameters and state of charge",
    )
    battery_state: Optional[Dict[str, Any]] = Field(default=None, description="Alias for battery availability")
    risk_results: Optional[Dict[str, Any]] = Field(default=None, description="Risk assessment output to factor into reliability constraints")
    operational_constraints: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"max_line_utilization": 0.90},
        description="Transmission thermal flow and spinning reserve constraints",
    )
    critical_load_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"prioritize_critical": True, "critical_demand_mw": 45.0},
        description="Critical load preservation requirements",
    )


# Aliases for backward compatibility
OptimizationRequest = OptimizationRunRequest


class OptimizationRunResponse(BaseModel):
    optimization_status: str = Field(default="optimal", description="Solver status: optimal, feasible, completed")
    objective: OptimizationObjective = Field(..., description="Solved objective function")
    recommended_actions: List[str] = Field(
        default_factory=list,
        description="Actionable operational recommendations for grid operators",
    )
    generator_dispatch: List[GeneratorDispatch] = Field(..., description="Optimal dispatch schedules per generating unit")
    total_dispatched_generation_mw: float = Field(..., description="Total active generation dispatched in MW")
    battery_dispatch_mw: float = Field(..., description="Scheduled battery flow in MW (+ discharge, - charge)")
    battery_charge_discharge_mw: float = Field(..., description="Alias for battery_dispatch_mw")
    backup_generation_mw: float = Field(default=0.0, description="Scheduled emergency backup generator capacity in MW")
    flexible_load_reduction_mw: float = Field(default=0.0, description="Scheduled demand response or flexible load curtailment in MW")
    renewable_curtailment_mw: float = Field(default=0.0, description="Amount of renewable energy curtailed in MW")
    unserved_demand_mw: float = Field(default=0.0, description="Amount of unserved load / load shedding in MW")
    expected_risk_reduction: float = Field(
        default=0.18,
        description="Estimated operational risk reduction achieved by applying optimal dispatch",
    )
    objective_value: float = Field(..., description="Optimized objective function score")
    cost_estimate_usd: float = Field(..., description="Total estimated hourly operating cost in USD")
    model_source: str = Field(
        default="ai_module",
        description="Optimization engine source: ai_module or service_fallback",
        json_schema_extra={"example": "ai_module"},
    )
    summary: Dict[str, Any] = Field(default_factory=dict, description="Key optimization metrics and solver statistics")
    solved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Optimization solver completion timestamp",
    )


# Aliases for backward compatibility
OptimizationResponse = OptimizationRunResponse
