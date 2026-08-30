"""
PULSEiQ - Data Models for Demand Anomaly Detection.
Defines structured result containers and observation points.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AnomalyStatus(str, Enum):
    """Observation status classification."""
    NORMAL = "NORMAL"
    ANOMALY = "ANOMALY"


@dataclass
class AnomalyPoint:
    """An individual time-series observation with anomaly classification."""
    timestamp: str
    observed_demand: float
    anomaly_flag: bool
    anomaly_score: float
    status: str  # "NORMAL" or "ANOMALY"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnomalyDetectionResult:
    """Complete summary of anomaly detection analysis across a time-series evaluation."""
    total_observations: int
    anomalies_detected: int
    anomaly_rate_pct: float
    points: List[AnomalyPoint] = field(default_factory=list)
    model_name: str = "IsolationForest"
    contamination: float = 0.03

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_observations": self.total_observations,
            "anomalies_detected": self.anomalies_detected,
            "anomaly_rate_pct": self.anomaly_rate_pct,
            "model_name": self.model_name,
            "contamination": self.contamination,
            "points": [p.to_dict() for p in self.points],
        }
