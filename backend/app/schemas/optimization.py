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
    battery_state: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"soc_percent": 78.5, "capacity_mw": 80.0, "allow_discharge": True},
        description="Current battery asset parameters",
    )
    transmission_constraints: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"max_line_utilization": 0.90},
        description="Transmission thermal flow constraints",
    )
    critical_load_requirements: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"prioritize_critical": True, "critical_demand_mw": 45.0},
        description="Reliability and critical load constraints",
    )


# Maintain alias for backward compatibility
OptimizationRequest = OptimizationRunRequest


class OptimizationRunResponse(BaseModel):
    optimization_status: str = Field(default="optimal", description="Solver status: optimal, feasible, completed")
    objective: OptimizationObjective = Field(..., description="Solved objective function")
    generator_dispatch: List[GeneratorDispatch] = Field(..., description="Optimal dispatch schedules per generating unit")
    total_dispatched_generation_mw: float = Field(..., description="Total active generation dispatched in MW")
    battery_charge_discharge_mw: float = Field(..., description="Scheduled battery flow in MW (+ discharge, - charge)")
    renewable_curtailment_mw: float = Field(default=0.0, description="Amount of renewable energy curtailed in MW")
    unserved_demand_mw: float = Field(default=0.0, description="Amount of unserved load / load shedding in MW")
    objective_value: float = Field(..., description="Optimized objective function score")
    cost_estimate_usd: float = Field(..., description="Total estimated hourly operating cost in USD")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Key optimization metrics and solver statistics")
    solved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Optimization solver completion timestamp",
    )


# Maintain alias for backward compatibility
OptimizationResponse = OptimizationRunResponse
