"""
PULSEiQ - Risk Assessment Data Models & Structured Contingency Results.
Typed representations for N-1/N-k screening, cascading failure dynamics,
vulnerability indices, and overall grid risk scorecards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(str, Enum):
    """Categorical risk index level."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EXTREME = "EXTREME"


class ContingencyType(str, Enum):
    """Type of contingency event."""
    N_MINUS_1_LINE = "N-1 Line Outage"
    N_MINUS_1_GEN = "N-1 Generator Outage"
    N_MINUS_K = "N-k Multi-Asset Outage"
    CASCADING = "Cascading Failure Event"


@dataclass
class ContingencyResult:
    """Detailed evaluation result for a specific N-1 or N-k contingency."""
    contingency_id: str
    tripped_components: List[str]
    contingency_type: ContingencyType
    is_secure: bool
    unserved_load_mw: float
    critical_load_affected_mw: float
    critical_load_at_risk: bool
    overloaded_lines: List[str] = field(default_factory=list)
    max_line_utilization_pct: float = 0.0
    isolated_nodes: List[str] = field(default_factory=list)
    frequency_hz: float = 60.0
    severity_score: float = 0.0  # 0 to 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contingency_id": self.contingency_id,
            "tripped_components": list(self.tripped_components),
            "contingency_type": self.contingency_type.value,
            "is_secure": self.is_secure,
            "unserved_load_mw": round(self.unserved_load_mw, 3),
            "critical_load_affected_mw": round(self.critical_load_affected_mw, 3),
            "critical_load_at_risk": self.critical_load_at_risk,
            "overloaded_lines": list(self.overloaded_lines),
            "max_line_utilization_pct": round(self.max_line_utilization_pct, 2),
            "isolated_nodes": list(self.isolated_nodes),
            "frequency_hz": round(self.frequency_hz, 4),
            "severity_score": round(self.severity_score, 2),
        }


@dataclass
class CascadingStage:
    """Telemetry captured at a single stage of a cascading failure progression."""
    stage_index: int
    newly_tripped_lines: List[str]
    overloaded_lines_before_trip: List[str]
    unserved_load_mw: float
    system_frequency_hz: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_index": self.stage_index,
            "newly_tripped_lines": list(self.newly_tripped_lines),
            "overloaded_lines_before_trip": list(self.overloaded_lines_before_trip),
            "unserved_load_mw": round(self.unserved_load_mw, 3),
            "system_frequency_hz": round(self.system_frequency_hz, 4),
        }


@dataclass
class CascadingFailureReport:
    """Report tracking cascading thermal overload propagation until stabilization or collapse."""
    initiating_contingency: List[str]
    total_stages: int
    stages: List[CascadingStage] = field(default_factory=list)
    final_unserved_mw: float = 0.0
    final_critical_unserved_mw: float = 0.0
    blackout_occurred: bool = False
    total_lines_lost: int = 0
    cascade_risk_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initiating_contingency": list(self.initiating_contingency),
            "total_stages": self.total_stages,
            "final_unserved_mw": round(self.final_unserved_mw, 3),
            "final_critical_unserved_mw": round(self.final_critical_unserved_mw, 3),
            "blackout_occurred": self.blackout_occurred,
            "total_lines_lost": self.total_lines_lost,
            "cascade_risk_score": round(self.cascade_risk_score, 2),
            "stages": [s.to_dict() for s in self.stages],
        }


@dataclass
class GridRiskAssessment:
    """
    Standardized, high-level grid risk scorecard ready for consumption by the FastAPI backend.
    """
    risk_index: float  # Normalized 0.0 to 1.0
    risk_level: RiskLevel
    failed_components: List[str]
    affected_load_mw: float
    critical_load_at_risk: bool
    n_1_violations_count: int
    most_critical_contingencies: List[ContingencyResult] = field(default_factory=list)
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
            "n_1_violations_count": self.n_1_violations_count,
            "cascading_risk_score": round(self.cascading_risk_score, 2),
            "most_critical_contingencies": [c.to_dict() for c in self.most_critical_contingencies],
            "vulnerable_assets": list(self.vulnerable_assets),
            "summary": dict(self.summary),
        }
