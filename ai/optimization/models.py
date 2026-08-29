"""
PULSEiQ - Optimization Models & Dispatch Result Schemas.
Typed specifications for economic dispatch configurations, unit commitment variables,
battery scheduling constraints, and structured optimization outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class OptimizationStatus(str, Enum):
    """Solver termination status."""
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    ERROR = "ERROR"


@dataclass
class OptimizationConfig:
    """Configurable cost coefficients and penalty weights for economic dispatch."""
    fuel_cost_per_mwh: Dict[str, float] = field(
        default_factory=lambda: {
            "gas_ccgt": 45.0,
            "conventional": 50.0,
            "solar": 0.0,
            "wind": 0.0,
            "battery": 8.0,
        }
    )
    normal_load_shedding_penalty: float = 500.0       # $ / MWh for normal load shedding
    critical_load_shedding_penalty: float = 15000.0   # $ / MWh for critical load (Hospital, Data Center)
    renewable_curtailment_penalty: float = 35.0       # $ / MWh for wasted renewable generation
    battery_cycle_cost: float = 10.0                  # $ / MWh degradation cost
    enforce_line_limits: bool = True
    time_step_hours: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fuel_cost_per_mwh": dict(self.fuel_cost_per_mwh),
            "normal_load_shedding_penalty": self.normal_load_shedding_penalty,
            "critical_load_shedding_penalty": self.critical_load_shedding_penalty,
            "renewable_curtailment_penalty": self.renewable_curtailment_penalty,
            "battery_cycle_cost": self.battery_cycle_cost,
            "enforce_line_limits": self.enforce_line_limits,
            "time_step_hours": self.time_step_hours,
        }


@dataclass
class DispatchResult:
    """Structured result of the optimal power dispatch solver."""
    status: OptimizationStatus
    total_cost: float
    generator_dispatch_mw: Dict[str, float] = field(default_factory=dict)
    battery_dispatch_mw: Dict[str, float] = field(default_factory=dict)  # + is discharge, - is charge
    battery_soc_after_pct: Dict[str, float] = field(default_factory=dict)
    curtailed_renewable_mw: Dict[str, float] = field(default_factory=dict)
    unserved_demand_mw: Dict[str, float] = field(default_factory=dict)
    critical_unserved_mw: float = 0.0
    critical_load_served_pct: float = 100.0
    total_generation_dispatched_mw: float = 0.0
    total_demand_served_mw: float = 0.0
    line_flows_mw: Dict[str, float] = field(default_factory=dict)
    line_utilizations_pct: Dict[str, float] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "total_cost": round(self.total_cost, 2),
            "total_generation_dispatched_mw": round(self.total_generation_dispatched_mw, 3),
            "total_demand_served_mw": round(self.total_demand_served_mw, 3),
            "critical_unserved_mw": round(self.critical_unserved_mw, 3),
            "critical_load_served_pct": round(self.critical_load_served_pct, 2),
            "generator_dispatch_mw": {k: round(v, 3) for k, v in self.generator_dispatch_mw.items()},
            "battery_dispatch_mw": {k: round(v, 3) for k, v in self.battery_dispatch_mw.items()},
            "battery_soc_after_pct": {k: round(v, 2) for k, v in self.battery_soc_after_pct.items()},
            "curtailed_renewable_mw": {k: round(v, 3) for k, v in self.curtailed_renewable_mw.items()},
            "unserved_demand_mw": {k: round(v, 3) for k, v in self.unserved_demand_mw.items()},
            "line_flows_mw": {k: round(v, 3) for k, v in self.line_flows_mw.items()},
            "line_utilizations_pct": {k: round(v, 2) for k, v in self.line_utilizations_pct.items()},
            "summary": dict(self.summary),
        }
