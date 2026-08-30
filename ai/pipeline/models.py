"""
PULSEiQ - Unified AI/ML Prediction & Risk Pipeline Data Models.
Typed representations for pipeline configuration, inputs, section results,
and unified output contracts ready for FastAPI backend consumption.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ai.models.grid import ElectricityGrid
from ai.risk.models import RiskLevel


@dataclass
class PipelineConfig:
    """Execution options for GridIntelligencePipeline."""
    forecast_horizon_hours: int = 24
    include_simulation: bool = True
    include_monte_carlo: bool = False
    monte_carlo_trials: int = 50
    include_contingency_screening: bool = True
    include_cascading_analysis: bool = True
    n_1_top_k: int = 5
    ranked_components_top_k: int = 5
    cascading_trigger_lines: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "forecast_horizon_hours": self.forecast_horizon_hours,
            "include_simulation": self.include_simulation,
            "include_monte_carlo": self.include_monte_carlo,
            "monte_carlo_trials": self.monte_carlo_trials,
            "include_contingency_screening": self.include_contingency_screening,
            "include_cascading_analysis": self.include_cascading_analysis,
            "n_1_top_k": self.n_1_top_k,
            "ranked_components_top_k": self.ranked_components_top_k,
            "cascading_trigger_lines": list(self.cascading_trigger_lines) if self.cascading_trigger_lines else None,
        }


@dataclass
class PipelineInput:
    """Container for input grid model, live telemetry, and pipeline configuration."""
    grid: ElectricityGrid
    telemetry: Optional[Dict[str, Any]] = None
    config: PipelineConfig = field(default_factory=PipelineConfig)
    timestamp: Optional[datetime] = None


@dataclass
class ForecastSection:
    """Multi-horizon forecasting predictions for demand, renewables, and net load."""
    horizon_hours: int
    load_forecast_mw: List[float]
    solar_forecast_mw: List[float]
    wind_forecast_mw: List[float]
    net_load_forecast_mw: List[float]
    total_forecasted_demand_mwh: float
    total_forecasted_renewable_mwh: float
    peak_demand_mw: float
    peak_net_load_mw: float
    renewable_penetration_pct: float
    timestamps: List[str] = field(default_factory=list)
    time_series_points: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "horizon_hours": self.horizon_hours,
            "load_forecast_mw": [round(x, 2) for x in self.load_forecast_mw],
            "solar_forecast_mw": [round(x, 2) for x in self.solar_forecast_mw],
            "wind_forecast_mw": [round(x, 2) for x in self.wind_forecast_mw],
            "net_load_forecast_mw": [round(x, 2) for x in self.net_load_forecast_mw],
            "total_forecasted_demand_mwh": round(self.total_forecasted_demand_mwh, 2),
            "total_forecasted_renewable_mwh": round(self.total_forecasted_renewable_mwh, 2),
            "peak_demand_mw": round(self.peak_demand_mw, 2),
            "peak_net_load_mw": round(self.peak_net_load_mw, 2),
            "renewable_penetration_pct": round(self.renewable_penetration_pct, 2),
            "timestamps": list(self.timestamps),
            "time_series_points": list(self.time_series_points),
        }


@dataclass
class RiskSection:
    """Structured grid risk assessment results."""
    score: float  # 0.0 to 1.0
    level: str    # LOW, MODERATE, HIGH, CRITICAL
    factors: Dict[str, float]
    n_1_violations_count: int
    critical_load_at_risk: bool
    affected_load_mw: float
    cascading_risk_score: float
    most_critical_contingencies: List[Dict[str, Any]] = field(default_factory=list)
    cascading_report: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "level": self.level,
            "factors": {k: round(v, 4) for k, v in self.factors.items()},
            "n_1_violations_count": self.n_1_violations_count,
            "critical_load_at_risk": self.critical_load_at_risk,
            "affected_load_mw": round(self.affected_load_mw, 3),
            "cascading_risk_score": round(self.cascading_risk_score, 2),
            "most_critical_contingencies": list(self.most_critical_contingencies),
            "cascading_report": dict(self.cascading_report) if self.cascading_report else None,
        }


@dataclass
class TopologySection:
    """NetworkX topological analytics and structural vulnerability summary."""
    node_count: int
    edge_count: int
    is_connected: bool
    connected_components_count: int
    density: float
    average_degree: float
    critical_nodes: List[Dict[str, Any]] = field(default_factory=list)
    articulation_points: List[str] = field(default_factory=list)
    bridges: List[List[str]] = field(default_factory=list)
    isolated_nodes: List[str] = field(default_factory=list)
    isolated_load_nodes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "is_connected": self.is_connected,
            "connected_components_count": self.connected_components_count,
            "density": round(self.density, 4),
            "average_degree": round(self.average_degree, 2),
            "critical_nodes": list(self.critical_nodes),
            "articulation_points": list(self.articulation_points),
            "bridges": list(self.bridges),
            "isolated_nodes": list(self.isolated_nodes),
            "isolated_load_nodes": list(self.isolated_load_nodes),
        }


@dataclass
class SimulationSection:
    """Physical power flow and probabilistic reliability indicators."""
    power_flow_converged: bool
    total_generation_mw: float
    total_demand_mw: float
    unserved_load_mw: float
    frequency_hz: float
    is_frequency_stable: bool
    max_line_utilization_pct: float
    overloaded_lines_count: int
    loss_of_load_probability: Optional[float] = None
    expected_unserved_energy_mwh: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "power_flow_converged": self.power_flow_converged,
            "total_generation_mw": round(self.total_generation_mw, 2),
            "total_demand_mw": round(self.total_demand_mw, 2),
            "unserved_load_mw": round(self.unserved_load_mw, 3),
            "frequency_hz": round(self.frequency_hz, 4),
            "is_frequency_stable": self.is_frequency_stable,
            "max_line_utilization_pct": round(self.max_line_utilization_pct, 2),
            "overloaded_lines_count": self.overloaded_lines_count,
            "loss_of_load_probability": round(self.loss_of_load_probability, 4) if self.loss_of_load_probability is not None else None,
            "expected_unserved_energy_mwh": round(self.expected_unserved_energy_mwh, 3) if self.expected_unserved_energy_mwh is not None else None,
        }


@dataclass
class PipelineMetadata:
    """Metadata tracking execution details and schema versioning."""
    grid_id: str
    grid_name: str
    timestamp: str
    pipeline_version: str = "1.0.0"
    execution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_id": self.grid_id,
            "grid_name": self.grid_name,
            "timestamp": self.timestamp,
            "pipeline_version": self.pipeline_version,
            "execution_time_ms": round(self.execution_time_ms, 2),
        }


@dataclass
class GridIntelligenceResult:
    """
    Standardized, unified prediction and risk output from GridIntelligencePipeline.
    Ready for FastAPI JSON serialization.
    """
    forecast: ForecastSection
    risk: RiskSection
    topology: TopologySection
    simulation: SimulationSection
    ranked_critical_components: List[Dict[str, Any]]
    metadata: PipelineMetadata
    status: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "forecast": self.forecast.to_dict(),
            "risk": self.risk.to_dict(),
            "topology": self.topology.to_dict(),
            "simulation": self.simulation.to_dict(),
            "ranked_critical_components": list(self.ranked_critical_components),
            "metadata": self.metadata.to_dict(),
        }
