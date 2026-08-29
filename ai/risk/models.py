"""
PULSEiQ - Risk Assessment Data Models & Structured Contingency Results.
Typed representations for N-1/N-k screening, cascading failure dynamics,
component criticality ranking, and normalized grid risk scorecards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class RiskLevel(str, Enum):
    """Categorical risk index level."""
    LOW = "LOW"            # 0.00 - 0.25
    MODERATE = "MODERATE"  # 0.25 - 0.50
    HIGH = "HIGH"          # 0.50 - 0.75
    CRITICAL = "CRITICAL"  # 0.75 - 1.00


class ContingencyType(str, Enum):
    """Type of contingency event."""
    N_MINUS_1_LINE = "N-1 Line Outage"
    N_MINUS_1_GEN = "N-1 Generator Outage"
    N_MINUS_1_COMPONENT = "N-1 Major Component Outage"
    N_MINUS_K = "N-k Multi-Asset Outage"
    CASCADING = "Cascading Failure Event"


@dataclass
class RiskThresholds:
    """Standardized risk level boundary thresholds (0.0 to 1.0)."""
    LOW_MAX: float = 0.25
    MODERATE_MAX: float = 0.50
    HIGH_MAX: float = 0.75
    CRITICAL_MAX: float = 1.00

    @classmethod
    def get_risk_level(cls, score: float) -> RiskLevel:
        """Map normalized numerical score (0.0 to 1.0) to categorical RiskLevel."""
        if score < cls.LOW_MAX:
            return RiskLevel.LOW
        elif score < cls.MODERATE_MAX:
            return RiskLevel.MODERATE
        elif score < cls.HIGH_MAX:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL


@dataclass
class RiskWeightsConfig:
    """Configurable factor weights for composite grid risk index calculation."""
    n1_vulnerability_weight: float = 0.25
    line_loading_weight: float = 0.20
    critical_load_exposure_weight: float = 0.20
    generation_reserve_weight: float = 0.15
    renewable_variability_weight: float = 0.10
    battery_storage_weight: float = 0.05
    voltage_frequency_weight: float = 0.05

    def to_dict(self) -> Dict[str, float]:
        return {
            "n1_vulnerability_weight": self.n1_vulnerability_weight,
            "line_loading_weight": self.line_loading_weight,
            "critical_load_exposure_weight": self.critical_load_exposure_weight,
            "generation_reserve_weight": self.generation_reserve_weight,
            "renewable_variability_weight": self.renewable_variability_weight,
            "battery_storage_weight": self.battery_storage_weight,
            "voltage_frequency_weight": self.voltage_frequency_weight,
        }


@dataclass
class ComponentCriticality:
    """Ranked criticality and vulnerability profile for an individual grid component."""
    component_id: str
    component_name: str
    component_type: str  # "generator", "line", "substation", "solar", "wind", "battery", "load"
    risk_score: float    # 0 to 100
    centrality_score: float  # Structural betweenness / degree centrality
    utilization_pct: float
    critical_load_exposure_mw: float  # MW of critical load dependent on this component
    is_critical: bool
    is_articulation_point: bool = False
    is_bridge: bool = False
    overall_criticality_rank: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_name": self.component_name,
            "component_type": self.component_type,
            "risk_score": round(self.risk_score, 2),
            "centrality_score": round(self.centrality_score, 4),
            "utilization_pct": round(self.utilization_pct, 2),
            "critical_load_exposure_mw": round(self.critical_load_exposure_mw, 3),
            "is_critical": self.is_critical,
            "is_articulation_point": self.is_articulation_point,
            "is_bridge": self.is_bridge,
            "overall_criticality_rank": self.overall_criticality_rank,
            "metadata": dict(self.metadata),
        }


@dataclass
class ConnectivitySummary:
    """Graph connectivity metrics post-contingency."""
    is_connected: bool = True
    connected_components_count: int = 1
    isolated_nodes: List[str] = field(default_factory=list)
    isolated_critical_loads: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_connected": self.is_connected,
            "connected_components_count": self.connected_components_count,
            "isolated_nodes": list(self.isolated_nodes),
            "isolated_critical_loads": list(self.isolated_critical_loads),
        }


@dataclass
class ContingencyResult:
    """Detailed evaluation result for an N-1 or N-k contingency."""
    contingency_id: str
    tripped_components: List[str]
    contingency_type: ContingencyType
    is_grid_operational: bool = True
    is_secure: bool = True
    affected_components: List[str] = field(default_factory=list)
    connectivity: ConnectivitySummary = field(default_factory=ConnectivitySummary)
    overloaded_components: List[Dict[str, Any]] = field(default_factory=list)
    unserved_load_mw: float = 0.0
    critical_load_affected_mw: float = 0.0
    critical_load_at_risk: bool = False
    max_line_utilization_pct: float = 0.0
    frequency_hz: float = 60.0
    risk_score: float = 0.0  # 0 to 100
    severity: str = "LOW"   # LOW, MODERATE, HIGH, CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contingency_id": self.contingency_id,
            "tripped_components": list(self.tripped_components),
            "contingency_type": self.contingency_type.value,
            "is_grid_operational": self.is_grid_operational,
            "is_secure": self.is_secure,
            "affected_components": list(self.affected_components),
            "connectivity": self.connectivity.to_dict(),
            "overloaded_components": list(self.overloaded_components),
            "unserved_load_mw": round(self.unserved_load_mw, 3),
            "critical_load_affected_mw": round(self.critical_load_affected_mw, 3),
            "critical_load_at_risk": self.critical_load_at_risk,
            "max_line_utilization_pct": round(self.max_line_utilization_pct, 2),
            "frequency_hz": round(self.frequency_hz, 4),
            "risk_score": round(self.risk_score, 2),
            "severity": self.severity,
        }


@dataclass
class CascadingStage:
    """Telemetry captured at a single sequential stage of a cascading failure progression."""
    stage_index: int
    tripped_in_this_stage: List[str]
    overloaded_lines_detected: List[str]
    unserved_load_mw: float
    critical_unserved_mw: float
    system_frequency_hz: float
    is_stable: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_index": self.stage_index,
            "tripped_in_this_stage": list(self.tripped_in_this_stage),
            "overloaded_lines_detected": list(self.overloaded_lines_detected),
            "unserved_load_mw": round(self.unserved_load_mw, 3),
            "critical_unserved_mw": round(self.critical_unserved_mw, 3),
            "system_frequency_hz": round(self.system_frequency_hz, 4),
            "is_stable": self.is_stable,
        }


@dataclass
class CascadingFailureReport:
    """Report tracking cascading thermal overload propagation from initiating trip to stabilization or collapse."""
    initiating_contingency: List[str]
    total_stages: int
    stages: List[CascadingStage] = field(default_factory=list)
    initial_failure: List[str] = field(default_factory=list)
    secondary_failures: List[str] = field(default_factory=list)
    final_state: Dict[str, Any] = field(default_factory=dict)
    final_unserved_mw: float = 0.0
    final_critical_unserved_mw: float = 0.0
    blackout_occurred: bool = False
    total_lines_lost: int = 0
    cascade_risk_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initiating_contingency": list(self.initiating_contingency),
            "total_stages": self.total_stages,
            "initial_failure": list(self.initial_failure),
            "secondary_failures": list(self.secondary_failures),
            "final_unserved_mw": round(self.final_unserved_mw, 3),
            "final_critical_unserved_mw": round(self.final_critical_unserved_mw, 3),
            "blackout_occurred": self.blackout_occurred,
            "total_lines_lost": self.total_lines_lost,
            "cascade_risk_score": round(self.cascade_risk_score, 2),
            "final_state": dict(self.final_state),
            "stages": [s.to_dict() for s in self.stages],
        }


@dataclass
class GridRiskAssessment:
    """
    Standardized, high-level grid risk scorecard ready for consumption by the FastAPI backend.
    """
    risk_index: float  # Normalized 0.0 to 1.0 (0-0.25 LOW, 0.25-0.50 MODERATE, 0.50-0.75 HIGH, 0.75-1.00 CRITICAL)
    risk_level: RiskLevel
    failed_components: List[str]
    affected_load_mw: float
    critical_load_at_risk: bool
    risk_factors: Dict[str, float] = field(default_factory=dict)
    n_1_violations_count: int = 0
    most_critical_contingencies: List[ContingencyResult] = field(default_factory=list)
    ranked_critical_components: List[ComponentCriticality] = field(default_factory=list)
    cascading_risk_score: float = 0.0
    vulnerable_assets: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_index": round(self.risk_index, 4),
            "risk_level": self.risk_level.value,
            "failed_components": list(self.failed_components),
            "affected_load_mw": round(self.affected_load_mw, 3),
            "critical_load_at_risk": self.critical_load_at_risk,
            "risk_factors": {k: round(v, 4) for k, v in self.risk_factors.items()},
            "n_1_violations_count": self.n_1_violations_count,
            "cascading_risk_score": round(self.cascading_risk_score, 2),
            "most_critical_contingencies": [c.to_dict() for c in self.most_critical_contingencies],
            "ranked_critical_components": [rc.to_dict() for rc in self.ranked_critical_components],
            "vulnerable_assets": list(self.vulnerable_assets),
            "summary": dict(self.summary),
        }
