"""
PULSEiQ - Simulation Models & Result Data Structures.
Typed representations for power-flow results, bus voltage indicators,
system frequency response, and Monte Carlo probabilistic risk summaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LoadingStatus(str, Enum):
    """Transmission line loading classification."""
    NORMAL = "normal"        # 0 - 80%
    WARNING = "warning"      # 80 - 100%
    OVERLOADED = "overloaded"  # > 100%


@dataclass
class PowerFlowLineResult:
    """Power flow result for an individual transmission/distribution line."""
    line_id: str
    line_name: str
    source_node_id: str
    target_node_id: str
    flow_mw: float
    capacity_mw: float
    utilization_pct: float
    is_overloaded: bool
    status: LoadingStatus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line_id": self.line_id,
            "line_name": self.line_name,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "flow_mw": round(self.flow_mw, 3),
            "capacity_mw": round(self.capacity_mw, 3),
            "utilization_pct": round(self.utilization_pct, 2),
            "is_overloaded": self.is_overloaded,
            "status": self.status.value,
        }


@dataclass
class BusVoltageResult:
    """Voltage and angle telemetry for an individual grid bus."""
    node_id: str
    node_name: str
    voltage_kv: float
    voltage_pu: float
    angle_deg: float
    is_voltage_violation: bool  # Outside [0.95, 1.05] p.u.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "voltage_kv": round(self.voltage_kv, 3),
            "voltage_pu": round(self.voltage_pu, 4),
            "angle_deg": round(self.angle_deg, 3),
            "is_voltage_violation": self.is_voltage_violation,
        }


@dataclass
class SimulationResult:
    """Structured result of a grid simulation / power-flow run."""
    grid_id: str
    total_generation_mw: float
    total_demand_mw: float
    power_imbalance_mw: float
    frequency_hz: float
    is_frequency_stable: bool
    max_line_utilization_pct: float
    overloaded_lines_count: int
    unserved_load_mw: float
    line_results: Dict[str, PowerFlowLineResult] = field(default_factory=dict)
    bus_voltages: Dict[str, BusVoltageResult] = field(default_factory=dict)
    risk_indicators: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_id": self.grid_id,
            "total_generation_mw": round(self.total_generation_mw, 3),
            "total_demand_mw": round(self.total_demand_mw, 3),
            "power_imbalance_mw": round(self.power_imbalance_mw, 3),
            "frequency_hz": round(self.frequency_hz, 4),
            "is_frequency_stable": self.is_frequency_stable,
            "max_line_utilization_pct": round(self.max_line_utilization_pct, 2),
            "overloaded_lines_count": self.overloaded_lines_count,
            "unserved_load_mw": round(self.unserved_load_mw, 3),
            "line_results": {k: v.to_dict() for k, v in self.line_results.items()},
            "bus_voltages": {k: v.to_dict() for k, v in self.bus_voltages.items()},
            "risk_indicators": {k: round(v, 4) for k, v in self.risk_indicators.items()},
            "metadata": dict(self.metadata),
        }


@dataclass
class MonteCarloSummary:
    """Statistical summary of Monte Carlo probabilistic grid simulations."""
    iterations_count: int
    loss_of_load_probability: float  # LOLP (0.0 to 1.0)
    expected_unserved_energy_mwh: float  # EUE (MWh)
    loss_of_load_events: int
    overload_probability: float  # Probability of any line exceeding 100%
    worst_case_unserved_mw: float
    average_unserved_mw: float
    line_overload_probabilities: Dict[str, float] = field(default_factory=dict)
    asset_trip_frequencies: Dict[str, int] = field(default_factory=dict)
    risk_score: float = 0.0  # Normalized composite risk score (0 to 100)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "iterations_count": self.iterations_count,
            "loss_of_load_probability": round(self.loss_of_load_probability, 5),
            "expected_unserved_energy_mwh": round(self.expected_unserved_energy_mwh, 3),
            "loss_of_load_events": self.loss_of_load_events,
            "overload_probability": round(self.overload_probability, 5),
            "worst_case_unserved_mw": round(self.worst_case_unserved_mw, 3),
            "average_unserved_mw": round(self.average_unserved_mw, 3),
            "line_overload_probabilities": {
                k: round(v, 4) for k, v in self.line_overload_probabilities.items()
            },
            "asset_trip_frequencies": dict(self.asset_trip_frequencies),
            "risk_score": round(self.risk_score, 2),
        }


@dataclass
class MonteCarloDemandScenarioResult:
    """
    Statistical summary and scenario trajectories of Monte Carlo demand simulations
    generated from central XGBoost demand forecasts.
    """
    timestamps: List[str]
    expected_forecast: List[float]
    scenario_curves: List[List[float]]
    mean_scenario_demand: List[float]
    min_scenario_demand: List[float]
    max_scenario_demand: List[float]
    std_dev: List[float]
    percentiles: Dict[str, List[float]]
    num_scenarios: int
    horizon_hours: int
    uncertainty_std: float = 0.05
    seed: int = 42
    target_id: Optional[str] = None
    target_name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_name": self.target_name,
            "horizon_hours": self.horizon_hours,
            "num_scenarios": self.num_scenarios,
            "uncertainty_std": self.uncertainty_std,
            "seed": self.seed,
            "timestamps": list(self.timestamps),
            "expected_forecast": [round(v, 3) for v in self.expected_forecast],
            "mean_scenario_demand": [round(v, 3) for v in self.mean_scenario_demand],
            "min_scenario_demand": [round(v, 3) for v in self.min_scenario_demand],
            "max_scenario_demand": [round(v, 3) for v in self.max_scenario_demand],
            "std_dev": [round(v, 3) for v in self.std_dev],
            "percentiles": {
                k: [round(v, 3) for v in vals] for k, vals in self.percentiles.items()
            },
            "scenario_curves": [
                [round(v, 3) for v in curve] for curve in self.scenario_curves
            ],
        }

