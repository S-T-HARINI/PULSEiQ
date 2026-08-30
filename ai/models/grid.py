"""
PULSEiQ - Grid Data Model
Comprehensive, reusable data structures representing electricity network components,
transmission/distribution connections, operational telemetries, risk metrics, and scenario configurations.
"""

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class NodeType(str, Enum):
    """Types of nodes/components present in the electricity grid."""
    GENERATOR = "generator"
    SOLAR = "solar"
    WIND = "wind"
    BATTERY = "battery"
    SUBSTATION = "substation"
    LOAD_NORMAL = "load_normal"
    LOAD_CRITICAL = "load_critical"


class ComponentStatus(str, Enum):
    """Operational statuses for grid equipment."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    TRIPPED = "tripped"
    MAINTENANCE = "maintenance"


class CriticalityLevel(str, Enum):
    """Criticality ranking for risk and vulnerability assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskMetrics:
    """Risk-related parameters and vulnerability assessment for a grid component."""
    criticality: CriticalityLevel = CriticalityLevel.MEDIUM
    failure_probability: float = 0.01  # Value between 0.0 and 1.0 (hourly/daily baseline)
    risk_score: float = 1.0  # Computed or assigned risk rating (0 - 100)
    vulnerability_factor: float = 1.0  # Susceptibility multiplier to external events
    historical_failures_count: int = 0

    def calculate_expected_loss(self, base_impact: float = 100.0) -> float:
        """Calculate probabilistic expected loss."""
        criticality_weights = {
            CriticalityLevel.LOW: 1.0,
            CriticalityLevel.MEDIUM: 2.5,
            CriticalityLevel.HIGH: 5.0,
            CriticalityLevel.CRITICAL: 10.0,
        }
        weight = criticality_weights.get(self.criticality, 1.0)
        return self.failure_probability * base_impact * weight * self.vulnerability_factor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "criticality": self.criticality.value,
            "failure_probability": self.failure_probability,
            "risk_score": self.risk_score,
            "vulnerability_factor": self.vulnerability_factor,
            "historical_failures_count": self.historical_failures_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RiskMetrics:
        return cls(
            criticality=CriticalityLevel(data.get("criticality", CriticalityLevel.MEDIUM)),
            failure_probability=float(data.get("failure_probability", 0.01)),
            risk_score=float(data.get("risk_score", 1.0)),
            vulnerability_factor=float(data.get("vulnerability_factor", 1.0)),
            historical_failures_count=int(data.get("historical_failures_count", 0)),
        )


@dataclass
class OperationalData:
    """Operational telemetry and capacity parameters for a node."""
    generation_mw: float = 0.0
    demand_mw: float = 0.0
    renewable_generation_mw: float = 0.0
    max_capacity_mw: float = 0.0
    min_capacity_mw: float = 0.0
    voltage_kv: float = 13.8  # Nominal voltage level in kV
    voltage_pu: float = 1.0   # Per-unit voltage (0.95 - 1.05 normal)
    frequency_hz: float = 60.0  # Grid frequency in Hz

    # Battery-specific storage telemetry
    battery_soc_pct: float = 0.0  # State of Charge (0.0 to 100.0%)
    battery_capacity_mwh: float = 0.0  # Total energy capacity
    battery_max_power_mw: float = 0.0  # Max charge/discharge rate

    @property
    def net_power_mw(self) -> float:
        """Net active power injected into the grid (positive = supply, negative = load)."""
        return self.generation_mw - self.demand_mw

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generation_mw": self.generation_mw,
            "demand_mw": self.demand_mw,
            "renewable_generation_mw": self.renewable_generation_mw,
            "max_capacity_mw": self.max_capacity_mw,
            "min_capacity_mw": self.min_capacity_mw,
            "voltage_kv": self.voltage_kv,
            "voltage_pu": self.voltage_pu,
            "frequency_hz": self.frequency_hz,
            "battery_soc_pct": self.battery_soc_pct,
            "battery_capacity_mwh": self.battery_capacity_mwh,
            "battery_max_power_mw": self.battery_max_power_mw,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OperationalData:
        return cls(
            generation_mw=float(data.get("generation_mw", 0.0)),
            demand_mw=float(data.get("demand_mw", 0.0)),
            renewable_generation_mw=float(data.get("renewable_generation_mw", 0.0)),
            max_capacity_mw=float(data.get("max_capacity_mw", 0.0)),
            min_capacity_mw=float(data.get("min_capacity_mw", 0.0)),
            voltage_kv=float(data.get("voltage_kv", 13.8)),
            voltage_pu=float(data.get("voltage_pu", 1.0)),
            frequency_hz=float(data.get("frequency_hz", 60.0)),
            battery_soc_pct=float(data.get("battery_soc_pct", 0.0)),
            battery_capacity_mwh=float(data.get("battery_capacity_mwh", 0.0)),
            battery_max_power_mw=float(data.get("battery_max_power_mw", 0.0)),
        )


@dataclass
class GridNode:
    """Represents a node or component within the power grid."""
    id: str
    name: str
    node_type: NodeType
    status: ComponentStatus = ComponentStatus.ONLINE
    operational: OperationalData = field(default_factory=OperationalData)
    risk: RiskMetrics = field(default_factory=RiskMetrics)
    location: Optional[Dict[str, float]] = None  # e.g., {"lat": 37.77, "lon": -122.41}
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_operational(self) -> bool:
        """Check if component is currently contributing or available to the grid."""
        return self.status in (ComponentStatus.ONLINE, ComponentStatus.DEGRADED)

    @property
    def is_renewable(self) -> bool:
        """Check if node represents renewable generation source."""
        return self.node_type in (NodeType.SOLAR, NodeType.WIND)

    @property
    def is_critical(self) -> bool:
        """Check if node represents critical infrastructure or priority load."""
        return self.node_type == NodeType.LOAD_CRITICAL or self.risk.criticality == CriticalityLevel.CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "status": self.status.value,
            "operational": self.operational.to_dict(),
            "risk": self.risk.to_dict(),
            "location": self.location,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GridNode:
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", data["id"])),
            node_type=NodeType(data["node_type"]),
            status=ComponentStatus(data.get("status", ComponentStatus.ONLINE)),
            operational=OperationalData.from_dict(data.get("operational", {})),
            risk=RiskMetrics.from_dict(data.get("risk", {})),
            location=data.get("location"),
            tags=list(data.get("tags", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class TransmissionLine:
    """Represents a transmission or distribution line connecting two grid nodes."""
    id: str
    name: str
    source_node_id: str
    target_node_id: str
    capacity_mw: float
    current_flow_mw: float = 0.0
    resistance_ohm: float = 0.05
    reactance_ohm: float = 0.1
    status: ComponentStatus = ComponentStatus.ONLINE
    risk: RiskMetrics = field(default_factory=RiskMetrics)
    voltage_level_kv: float = 69.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def utilization(self) -> float:
        """Line utilization ratio (0.0 to 1.0+)."""
        if self.capacity_mw <= 0:
            return 0.0
        return abs(self.current_flow_mw) / self.capacity_mw

    @property
    def utilization_pct(self) -> float:
        """Line utilization percentage (0.0 to 100.0%+)."""
        return round(self.utilization * 100.0, 4)

    @property
    def is_overloaded(self) -> bool:
        """Check if power flow exceeds nominal line thermal capacity."""
        return self.utilization > 1.0

    @property
    def is_operational(self) -> bool:
        """Check if line is closed and transmitting power."""
        return self.status in (ComponentStatus.ONLINE, ComponentStatus.DEGRADED)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "capacity_mw": self.capacity_mw,
            "current_flow_mw": self.current_flow_mw,
            "resistance_ohm": self.resistance_ohm,
            "reactance_ohm": self.reactance_ohm,
            "status": self.status.value,
            "risk": self.risk.to_dict(),
            "voltage_level_kv": self.voltage_level_kv,
            "utilization_pct": round(self.utilization_pct, 2),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TransmissionLine:
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", data["id"])),
            source_node_id=str(data["source_node_id"]),
            target_node_id=str(data["target_node_id"]),
            capacity_mw=float(data["capacity_mw"]),
            current_flow_mw=float(data.get("current_flow_mw", 0.0)),
            resistance_ohm=float(data.get("resistance_ohm", 0.05)),
            reactance_ohm=float(data.get("reactance_ohm", 0.1)),
            status=ComponentStatus(data.get("status", ComponentStatus.ONLINE)),
            risk=RiskMetrics.from_dict(data.get("risk", {})),
            voltage_level_kv=float(data.get("voltage_level_kv", 69.0)),
            tags=list(data.get("tags", [])),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class ScenarioConfig:
    """Scenario adjustment parameters for what-if simulation and stress testing."""
    name: str = "Base Scenario"
    description: str = ""
    demand_multiplier: float = 1.0
    solar_multiplier: float = 1.0
    wind_multiplier: float = 1.0
    battery_availability: bool = True
    contingencies: List[str] = field(default_factory=list)  # IDs of components to trip/fail

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "demand_multiplier": self.demand_multiplier,
            "solar_multiplier": self.solar_multiplier,
            "wind_multiplier": self.wind_multiplier,
            "battery_availability": self.battery_availability,
            "contingencies": list(self.contingencies),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ScenarioConfig:
        return cls(
            name=str(data.get("name", "Base Scenario")),
            description=str(data.get("description", "")),
            demand_multiplier=float(data.get("demand_multiplier", 1.0)),
            solar_multiplier=float(data.get("solar_multiplier", 1.0)),
            wind_multiplier=float(data.get("wind_multiplier", 1.0)),
            battery_availability=bool(data.get("battery_availability", True)),
            contingencies=list(data.get("contingencies", [])),
        )


@dataclass
class ElectricityGrid:
    """
    Core electricity grid data model encapsulating all nodes, lines, and network state.
    Provides utility methods for network aggregation, scenario cloning, validation, and serialization.
    """
    grid_id: str = "grid_001"
    name: str = "Default Electricity Grid"
    description: str = ""
    nodes: Dict[str, GridNode] = field(default_factory=dict)
    lines: Dict[str, TransmissionLine] = field(default_factory=dict)
    active_scenario: Optional[ScenarioConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: GridNode) -> None:
        """Add or update a grid node."""
        self.nodes[node.id] = node

    def add_line(self, line: TransmissionLine) -> None:
        """Add or update a transmission line."""
        self.lines[line.id] = line

    def get_node(self, node_id: str) -> Optional[GridNode]:
        """Retrieve node by ID."""
        return self.nodes.get(node_id)

    def get_line(self, line_id: str) -> Optional[TransmissionLine]:
        """Retrieve line by ID."""
        return self.lines.get(line_id)

    def get_nodes_by_type(self, node_type: NodeType) -> List[GridNode]:
        """Retrieve all nodes matching a specific node type."""
        return [node for node in self.nodes.values() if node.node_type == node_type]

    def get_lines_connected_to(self, node_id: str) -> List[TransmissionLine]:
        """Retrieve all transmission lines connected to a specific node."""
        return [
            line for line in self.lines.values()
            if line.source_node_id == node_id or line.target_node_id == node_id
        ]

    # --- Summary Metrics & Aggregations ---

    @property
    def total_generation_mw(self) -> float:
        """Total active power generation currently produced across online generators & renewables."""
        return sum(
            node.operational.generation_mw
            for node in self.nodes.values()
            if node.is_operational and node.node_type in (NodeType.GENERATOR, NodeType.SOLAR, NodeType.WIND)
        )

    @property
    def total_demand_mw(self) -> float:
        """Total active power demand requested across online load nodes."""
        return sum(
            node.operational.demand_mw
            for node in self.nodes.values()
            if node.is_operational and node.node_type in (NodeType.LOAD_NORMAL, NodeType.LOAD_CRITICAL)
        )

    @property
    def total_renewable_generation_mw(self) -> float:
        """Total power generation from solar and wind assets."""
        return sum(
            node.operational.renewable_generation_mw or node.operational.generation_mw
            for node in self.nodes.values()
            if node.is_operational and node.is_renewable
        )

    @property
    def total_critical_demand_mw(self) -> float:
        """Total demand from critical infrastructure loads."""
        return sum(
            node.operational.demand_mw
            for node in self.nodes.values()
            if node.is_operational and node.node_type == NodeType.LOAD_CRITICAL
        )

    @property
    def total_storage_capacity_mwh(self) -> float:
        """Total energy storage capacity across battery systems."""
        return sum(
            node.operational.battery_capacity_mwh
            for node in self.nodes.values()
            if node.node_type == NodeType.BATTERY
        )

    @property
    def power_balance_mw(self) -> float:
        """Net system balance: Total Generation - Total Demand (MW)."""
        return self.total_generation_mw - self.total_demand_mw

    # --- Scenario Execution & Stress Testing ---

    def apply_scenario(self, scenario: ScenarioConfig) -> ElectricityGrid:
        """
        Produce a modified deep copy of the grid applying the given scenario adjustments
        (demand multipliers, renewable multipliers, battery state, and contingencies).
        """
        grid_copy = copy.deepcopy(self)
        grid_copy.active_scenario = scenario

        # 1. Apply node modifications
        for node in grid_copy.nodes.values():
            # Check for contingency trips
            if node.id in scenario.contingencies:
                node.status = ComponentStatus.TRIPPED
                node.operational.generation_mw = 0.0
                node.operational.demand_mw = 0.0
                continue

            if not node.is_operational:
                continue

            # Multipliers
            if node.node_type in (NodeType.LOAD_NORMAL, NodeType.LOAD_CRITICAL):
                node.operational.demand_mw *= scenario.demand_multiplier
            elif node.node_type == NodeType.SOLAR:
                node.operational.generation_mw = min(
                    node.operational.max_capacity_mw,
                    node.operational.generation_mw * scenario.solar_multiplier,
                )
                node.operational.renewable_generation_mw = node.operational.generation_mw
            elif node.node_type == NodeType.WIND:
                node.operational.generation_mw = min(
                    node.operational.max_capacity_mw,
                    node.operational.generation_mw * scenario.wind_multiplier,
                )
                node.operational.renewable_generation_mw = node.operational.generation_mw
            elif node.node_type == NodeType.BATTERY:
                if not scenario.battery_availability:
                    node.status = ComponentStatus.OFFLINE
                    node.operational.generation_mw = 0.0

        # 2. Apply line modifications & contingencies
        for line in grid_copy.lines.values():
            if line.id in scenario.contingencies:
                line.status = ComponentStatus.TRIPPED
                line.current_flow_mw = 0.0
            elif not line.is_operational:
                line.current_flow_mw = 0.0

        return grid_copy

    # --- Validation ---

    def validate_grid(self) -> List[str]:
        """Validate topological integrity and consistency of the grid network."""
        errors: List[str] = []
        node_ids: Set[str] = set(self.nodes.keys())

        if not self.nodes:
            errors.append("Grid contains no nodes.")

        for line_id, line in self.lines.items():
            if line.source_node_id not in node_ids:
                errors.append(f"Line '{line_id}' references unknown source_node_id '{line.source_node_id}'.")
            if line.target_node_id not in node_ids:
                errors.append(f"Line '{line_id}' references unknown target_node_id '{line.target_node_id}'.")
            if line.capacity_mw <= 0:
                errors.append(f"Line '{line_id}' has non-positive capacity ({line.capacity_mw} MW).")

        for node_id, node in self.nodes.items():
            if node.operational.max_capacity_mw < 0:
                errors.append(f"Node '{node_id}' has negative max capacity.")
            if node.operational.demand_mw < 0:
                errors.append(f"Node '{node_id}' has negative demand.")

        return errors

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        """Serialize grid to standard dictionary structure."""
        return {
            "grid_id": self.grid_id,
            "name": self.name,
            "description": self.description,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "lines": {lid: l.to_dict() for lid, l in self.lines.items()},
            "active_scenario": self.active_scenario.to_dict() if self.active_scenario else None,
            "metadata": dict(self.metadata),
            "summary": {
                "total_nodes": len(self.nodes),
                "total_lines": len(self.lines),
                "total_generation_mw": round(self.total_generation_mw, 2),
                "total_demand_mw": round(self.total_demand_mw, 2),
                "total_renewable_generation_mw": round(self.total_renewable_generation_mw, 2),
                "total_critical_demand_mw": round(self.total_critical_demand_mw, 2),
                "total_storage_capacity_mwh": round(self.total_storage_capacity_mwh, 2),
                "power_balance_mw": round(self.power_balance_mw, 2),
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ElectricityGrid:
        """Deserialize grid from dictionary structure."""
        nodes = {nid: GridNode.from_dict(ndata) for nid, ndata in data.get("nodes", {}).items()}
        lines = {lid: TransmissionLine.from_dict(ldata) for lid, ldata in data.get("lines", {}).items()}
        active_scenario = (
            ScenarioConfig.from_dict(data["active_scenario"])
            if data.get("active_scenario")
            else None
        )
        return cls(
            grid_id=str(data.get("grid_id", "grid_001")),
            name=str(data.get("name", "Default Electricity Grid")),
            description=str(data.get("description", "")),
            nodes=nodes,
            lines=lines,
            active_scenario=active_scenario,
            metadata=dict(data.get("metadata", {})),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize grid to JSON string format."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> ElectricityGrid:
        """Deserialize grid from JSON string."""
        return cls.from_dict(json.loads(json_str))
