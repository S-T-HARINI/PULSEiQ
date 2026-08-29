from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PipelineRunRequest(BaseModel):
    horizon_hours: int = Field(24, ge=1, le=168, description="Forecasting horizon in hours (1-168)", json_schema_extra={"example": 24})
    include_simulation: bool = Field(True, description="Whether to execute DC power-flow simulation")
    include_monte_carlo: bool = Field(False, description="Whether to execute Monte Carlo reliability analysis")
    monte_carlo_trials: int = Field(50, ge=1, le=500, description="Monte Carlo simulation iterations")
    include_contingency_screening: bool = Field(True, description="Whether to execute N-1 contingency screening")
    include_cascading_analysis: bool = Field(True, description="Whether to execute cascading failure simulation")
    include_optimization: bool = Field(True, description="Whether to execute optimal economic and carbon dispatch")
    optimization_objective: Optional[str] = Field("cost_minimization", description="Optimization objective: cost_minimization, emission_reduction, reliability_maximization")
    contingency_event: Optional[str] = Field(None, description="Forced line outage or contingency trigger", json_schema_extra={"example": "line-north-central-1"})
    load_growth_factor: Optional[float] = Field(1.0, ge=0.1, le=3.0, description="Load scaling multiplier", json_schema_extra={"example": 1.0})
    telemetry: Optional[Dict[str, Any]] = Field(default=None, description="Optional live telemetry overrides")
    grid_state: Optional[Dict[str, Any]] = Field(default=None, description="Custom grid topology override")


# Backward compatibility aliases
PipelineRequest = PipelineRunRequest


class PipelineRunResponse(BaseModel):
    status: str = Field(default="SUCCESS", description="Pipeline execution status", json_schema_extra={"example": "SUCCESS"})
    model_source: str = Field(default="ai_module", description="Engine used: ai_module or service_fallback", json_schema_extra={"example": "ai_module"})
    forecast: Dict[str, Any] = Field(..., description="Multi-horizon demand, solar, and wind forecasts")
    simulation: Dict[str, Any] = Field(..., description="DC power flow, frequency, and line utilization results")
    risk: Dict[str, Any] = Field(..., description="Multi-factor risk assessment, N-1 screening, and cascading analysis")
    optimization: Optional[Dict[str, Any]] = Field(None, description="Optimal dispatch allocations and unit commitment recommendations")
    topology: Dict[str, Any] = Field(..., description="Graph connectivity, density, and critical articulation points")
    ranked_critical_components: List[Dict[str, Any]] = Field(default_factory=list, description="Top vulnerable components ranked by risk impact")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Pipeline execution metadata and timing")


# Backward compatibility aliases
PipelineResponse = PipelineRunResponse
