"""
PULSEiQ - Graph Models & Structured Analysis Results.
Typed representations of network topological metrics, cut vertices, bridges,
isolated load sectors, and critical topological hubs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GraphAnalysisResult:
    """Comprehensive structured topology analysis of an electricity grid graph."""
    grid_id: str
    node_count: int
    edge_count: int
    is_connected: bool
    connected_components_count: int
    density: float
    average_degree: float
    degrees: Dict[str, int] = field(default_factory=dict)
    degree_centrality: Dict[str, float] = field(default_factory=dict)
    betweenness_centrality: Dict[str, float] = field(default_factory=dict)
    closeness_centrality: Dict[str, float] = field(default_factory=dict)
    articulation_points: List[str] = field(default_factory=list)
    bridges: List[Tuple[str, str]] = field(default_factory=list)
    isolated_nodes: List[str] = field(default_factory=list)
    isolated_load_nodes: List[str] = field(default_factory=list)
    critical_hubs: List[Dict[str, Any]] = field(default_factory=list)
    vulnerable_lines: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grid_id": self.grid_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "is_connected": self.is_connected,
            "connected_components_count": self.connected_components_count,
            "density": round(self.density, 4),
            "average_degree": round(self.average_degree, 2),
            "degrees": dict(self.degrees),
            "degree_centrality": {k: round(v, 4) for k, v in self.degree_centrality.items()},
            "betweenness_centrality": {k: round(v, 4) for k, v in self.betweenness_centrality.items()},
            "closeness_centrality": {k: round(v, 4) for k, v in self.closeness_centrality.items()},
            "articulation_points": list(self.articulation_points),
            "bridges": [list(b) for b in self.bridges],
            "isolated_nodes": list(self.isolated_nodes),
            "isolated_load_nodes": list(self.isolated_load_nodes),
            "critical_hubs": list(self.critical_hubs),
            "vulnerable_lines": list(self.vulnerable_lines),
            "summary": dict(self.summary),
        }
