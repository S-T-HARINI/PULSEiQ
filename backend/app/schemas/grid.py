from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    CONVENTIONAL_GENERATOR = "conventional_generator"
    SOLAR_PLANT = "solar_plant"
    WIND_PLANT = "wind_plant"
    BATTERY = "battery"
    SUBSTATION = "substation"
    LOAD = "load"
    CRITICAL_LOAD = "critical_load"


class NodeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    CONGESTED = "congested"


class NodeCriticality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EdgeStatus(str, Enum):
    NORMAL = "normal"
    CONGESTED = "congested"
    TRIPPED = "tripped"
    MAINTENANCE = "maintenance"


class GridNodePosition(BaseModel):
    x: Optional[float] = Field(None, description="X coordinate for 2D diagram visualization")
    y: Optional[float] = Field(None, description="Y coordinate for 2D diagram visualization")


class GridNode(BaseModel):
    id: str = Field(..., description="Unique node identifier", json_schema_extra={"example": "gen-gas-1"})
    name: str = Field(..., description="Human readable component name", json_schema_extra={"example": "Metro Combined Cycle Gas Turbine"})
    type: NodeType = Field(..., description="Type of grid asset")
    capacity_mw: float = Field(..., description="Maximum rated capacity in MW", ge=0.0)
    current_output_mw: float = Field(..., description="Current power output (generation) or power consumption (load) in MW")
    status: NodeStatus = Field(default=NodeStatus.ONLINE, description="Operational status of the node")
    criticality: NodeCriticality = Field(default=NodeCriticality.MEDIUM, description="Criticality level of node asset")
    utilization_percent: float = Field(default=0.0, description="Asset capacity utilization percentage (0-100%)", ge=0.0)
    risk_score: float = Field(default=0.1, description="Asset risk score (0.0=safe, 1.0=critical)", ge=0.0, le=1.0)
    latitude: Optional[float] = Field(None, description="Geographic latitude coordinate")
    longitude: Optional[float] = Field(None, description="Geographic longitude coordinate")
    position: Optional[GridNodePosition] = Field(None, description="Layout coordinates for frontend Grid Twin diagram")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional asset metadata")


class GridEdge(BaseModel):
    id: str = Field(..., description="Unique transmission line identifier", json_schema_extra={"example": "line-1-2"})
    source: str = Field(..., description="Source node identifier", json_schema_extra={"example": "gen-gas-1"})
    target: str = Field(..., description="Target node identifier", json_schema_extra={"example": "sub-central-1"})
    capacity_mw: float = Field(..., description="Maximum thermal line capacity in MW", ge=0.0)
    power_flow_mw: float = Field(..., description="Active power flow across line in MW")
    utilization_percent: float = Field(..., description="Thermal line loading percentage (0-100+%)", ge=0.0)
    status: EdgeStatus = Field(default=EdgeStatus.NORMAL, description="Transmission line operational status")
    risk_score: float = Field(default=0.1, description="Transmission line risk score (0.0=safe, 1.0=critical)", ge=0.0, le=1.0)
    resistance_ohms: Optional[float] = Field(None, description="Line electrical resistance in ohms")
    reactance_ohms: Optional[float] = Field(None, description="Line electrical reactance in ohms")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional transmission metadata")


class GridSummary(BaseModel):
    total_generation_mw: float = Field(..., description="Total active generation currently produced in MW", ge=0.0)
    total_demand_mw: float = Field(..., description="Total active load demand across all consumers in MW", ge=0.0)
    renewable_percentage: float = Field(..., description="Percentage of total generation supplied by renewables (solar/wind)", ge=0.0, le=100.0)
    battery_soc: float = Field(..., description="Aggregate Battery State of Charge percentage (0-100%)", ge=0.0, le=100.0)
    grid_risk_index: float = Field(..., description="Aggregated operational risk index (0.0=safe, 1.0=critical)", ge=0.0, le=1.0)
    active_contingencies_count: int = Field(default=0, description="Number of active line/node outages or warnings")
    net_power_balance_mw: float = Field(default=0.0, description="Generation minus demand balance in MW")


class GridResponse(BaseModel):
    nodes: List[GridNode] = Field(..., description="List of all grid nodes (generators, substations, loads, batteries)")
    edges: List[GridEdge] = Field(..., description="List of all transmission lines/edges connecting the nodes")
    summary: GridSummary = Field(..., description="Aggregated operational summary metrics")
    timestamp: Optional[str] = Field(None, description="ISO-8601 timestamp of grid state capture")
