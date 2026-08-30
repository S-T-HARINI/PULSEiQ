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
    current_output_mw: float = Field(default=0.0, description="Current power output (generation) or power consumption (load) in MW")
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
    capacity_mw: float = Field(..., description="Maximum thermal line capacity in MW")
    power_flow_mw: float = Field(default=0.0, description="Active power flow across line in MW")
    utilization_percent: float = Field(default=0.0, description="Thermal line loading percentage (0-100+%)")
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
    grid_id: Optional[str] = Field(default="reference_demo_grid", description="Grid identifier")
    name: Optional[str] = Field(default="PULSEiQ Regional Demonstration Grid", description="Grid human-readable name")
    is_reference: bool = Field(default=True, description="Whether this is the immutable reference demonstration grid")
    is_active: bool = Field(default=True, description="Whether this grid is currently active in the simulation")
    nodes: List[GridNode] = Field(..., description="List of all grid nodes (generators, substations, loads, batteries)")
    edges: List[GridEdge] = Field(..., description="List of all transmission lines/edges connecting the nodes")
    summary: GridSummary = Field(..., description="Aggregated operational summary metrics")
    timestamp: Optional[str] = Field(None, description="ISO-8601 timestamp of grid state capture")


class CustomGridCreate(BaseModel):
    """Schema for creating a new custom electricity grid / digital twin."""
    grid_id: Optional[str] = Field(None, description="Optional unique grid ID (auto-generated if omitted)")
    name: str = Field(..., description="Grid name", json_schema_extra={"example": "Microgrid Alpha"})
    description: Optional[str] = Field(default="", description="Detailed description of grid topology")
    nodes: List[GridNode] = Field(default_factory=list, description="List of grid nodes/components")
    edges: List[GridEdge] = Field(default_factory=list, description="List of transmission/distribution lines")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom grid metadata tags")


class CustomGridUpdate(BaseModel):
    """Schema for updating an existing custom electricity grid."""
    name: Optional[str] = Field(None, description="Updated grid name")
    description: Optional[str] = Field(None, description="Updated grid description")
    nodes: Optional[List[GridNode]] = Field(None, description="Replacement list of grid nodes")
    edges: Optional[List[GridEdge]] = Field(None, description="Replacement list of transmission lines")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class CustomGridSummary(BaseModel):
    """Summary overview schema for listing available reference and custom grids."""
    grid_id: str = Field(..., description="Unique grid identifier")
    name: str = Field(..., description="Grid display name")
    description: str = Field(default="", description="Grid description")
    is_reference: bool = Field(default=False, description="Whether this is the reference demo grid")
    is_active: bool = Field(default=False, description="Whether this grid is currently selected as active")
    node_count: int = Field(..., description="Number of buses/nodes in grid")
    edge_count: int = Field(..., description="Number of transmission branches in grid")
    total_generation_mw: float = Field(default=0.0, description="Total generation capacity in MW")
    total_demand_mw: float = Field(default=0.0, description="Total demand load in MW")
    created_at: Optional[str] = Field(None, description="Timestamp of grid creation")
    updated_at: Optional[str] = Field(None, description="Timestamp of last update")


class GridDetailResponse(BaseModel):
    """Detailed response schema for an individual grid (reference or custom)."""
    grid_id: str = Field(..., description="Unique grid identifier")
    name: str = Field(..., description="Grid display name")
    description: str = Field(default="", description="Grid description")
    is_reference: bool = Field(default=False, description="Whether this is the reference demo grid")
    is_active: bool = Field(default=False, description="Whether this grid is currently active")
    nodes: List[GridNode] = Field(default_factory=list, description="List of grid nodes")
    edges: List[GridEdge] = Field(default_factory=list, description="List of transmission edges")
    summary: GridSummary = Field(..., description="Operational summary metrics")
    validation_errors: List[str] = Field(default_factory=list, description="Topological validation warning/error list")
    timestamp: Optional[str] = Field(None, description="Timestamp of response")


class GridActivationResponse(BaseModel):
    """Response schema after activating a grid."""
    status: str = Field(default="activated", description="Status outcome")
    active_grid_id: str = Field(..., description="Activated grid ID")
    active_grid_name: str = Field(..., description="Activated grid display name")
    is_reference: bool = Field(default=False, description="Whether active grid is reference")
    message: str = Field(..., description="Human-readable confirmation message")

