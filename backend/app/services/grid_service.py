from datetime import datetime, timezone
from typing import List, Optional, Set
from backend.app.schemas.grid import (
    NodeType,
    NodeStatus,
    NodeCriticality,
    EdgeStatus,
    GridNodePosition,
    GridNode,
    GridEdge,
    GridSummary,
    GridResponse,
)


class GridService:
    """Service providing realistic electricity grid topology, asset states, and telemetry.
    Acts as the single source of truth for the Grid Twin, designed for seamless handoff
    to power-flow and simulation engines.
    """

    def __init__(self) -> None:
        self._nodes: List[GridNode] = [
            # Conventional Generation
            GridNode(
                id="gen-gas-1",
                name="Metro Gas Combined-Cycle Plant",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=350.0,
                current_output_mw=220.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=62.86,
                risk_score=0.12,
                latitude=37.7749,
                longitude=-122.4194,
                position=GridNodePosition(x=120.0, y=100.0),
                metadata={"fuel_type": "natural_gas", "heat_rate_btu_kwh": 6800, "ramp_rate_mw_min": 15.0},
            ),
            # Renewable Generation (Solar)
            GridNode(
                id="gen-solar-1",
                name="Highland Solar Photovoltaic Park",
                type=NodeType.SOLAR_PLANT,
                capacity_mw=180.0,
                current_output_mw=140.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=77.78,
                risk_score=0.18,
                latitude=37.8044,
                longitude=-122.2711,
                position=GridNodePosition(x=420.0, y=80.0),
                metadata={"inverter_efficiency": 0.98, "irradiance_w_m2": 850.0, "temperature_c": 28.0},
            ),
            # Renewable Generation (Wind)
            GridNode(
                id="gen-wind-1",
                name="Coastal Ridge Wind Farm",
                type=NodeType.WIND_PLANT,
                capacity_mw=150.0,
                current_output_mw=95.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=63.33,
                risk_score=0.22,
                latitude=37.8715,
                longitude=-122.2730,
                position=GridNodePosition(x=700.0, y=110.0),
                metadata={"turbine_count": 50, "avg_wind_speed_mps": 9.2, "cut_in_speed_mps": 3.0},
            ),
            # Battery Storage System (BESS)
            GridNode(
                id="bat-bess-1",
                name="Valley Grid Battery Storage System",
                type=NodeType.BATTERY,
                capacity_mw=80.0,
                current_output_mw=20.0,  # 20 MW active discharging
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=25.00,
                risk_score=0.10,
                latitude=37.6879,
                longitude=-122.4702,
                position=GridNodePosition(x=260.0, y=320.0),
                metadata={"capacity_mwh": 320.0, "state_of_charge_percent": 78.5, "mode": "discharging"},
            ),
            # Substations
            GridNode(
                id="sub-north-1",
                name="North Transmission Substation (230kV)",
                type=NodeType.SUBSTATION,
                capacity_mw=600.0,
                current_output_mw=0.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=63.33,
                risk_score=0.15,
                latitude=37.8200,
                longitude=-122.3500,
                position=GridNodePosition(x=280.0, y=180.0),
                metadata={"voltage_kv": 230.0, "transformer_status": "optimal"},
            ),
            GridNode(
                id="sub-central-1",
                name="Central Bulk Substation (230kV/115kV)",
                type=NodeType.SUBSTATION,
                capacity_mw=800.0,
                current_output_mw=0.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=71.25,
                risk_score=0.20,
                latitude=37.7600,
                longitude=-122.3800,
                position=GridNodePosition(x=500.0, y=240.0),
                metadata={"voltage_primary_kv": 230.0, "voltage_secondary_kv": 115.0},
            ),
            GridNode(
                id="sub-south-1",
                name="South Distribution Substation (115kV)",
                type=NodeType.SUBSTATION,
                capacity_mw=500.0,
                current_output_mw=0.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=65.00,
                risk_score=0.14,
                latitude=37.7000,
                longitude=-122.3900,
                position=GridNodePosition(x=620.0, y=360.0),
                metadata={"voltage_kv": 115.0, "busbar_status": "balanced"},
            ),
            # Normal Loads
            GridNode(
                id="load-industrial-1",
                name="East Harbor Industrial Zone",
                type=NodeType.LOAD,
                capacity_mw=220.0,
                current_output_mw=180.0,  # 180 MW load
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=81.82,
                risk_score=0.16,
                latitude=37.7400,
                longitude=-122.3200,
                position=GridNodePosition(x=780.0, y=260.0),
                metadata={"power_factor": 0.92, "sheddable": True},
            ),
            GridNode(
                id="load-residential-1",
                name="Metro Heights Residential District",
                type=NodeType.LOAD,
                capacity_mw=200.0,
                current_output_mw=150.0,  # 150 MW load
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.LOW,
                utilization_percent=75.00,
                risk_score=0.10,
                latitude=37.7300,
                longitude=-122.4400,
                position=GridNodePosition(x=150.0, y=420.0),
                metadata={"power_factor": 0.95, "smart_meter_count": 48500},
            ),
            GridNode(
                id="load-commercial-1",
                name="Downtown Financial Center",
                type=NodeType.LOAD,
                capacity_mw=120.0,
                current_output_mw=85.0,  # 85 MW load
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=70.83,
                risk_score=0.12,
                latitude=37.7900,
                longitude=-122.4000,
                position=GridNodePosition(x=420.0, y=420.0),
                metadata={"power_factor": 0.94, "peak_window": "09:00-18:00"},
            ),
            # Critical Load (Hospital)
            GridNode(
                id="load-hospital-metro",
                name="Metro University Hospital & Trauma Center",
                type=NodeType.CRITICAL_LOAD,
                capacity_mw=60.0,
                current_output_mw=45.0,  # 45 MW critical load
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=75.00,
                risk_score=0.08,
                latitude=37.7650,
                longitude=-122.4500,
                position=GridNodePosition(x=680.0, y=460.0),
                metadata={
                    "backup_generators_available": 3,
                    "backup_fuel_hours": 72.0,
                    "life_support_priority": True,
                },
            ),
        ]

        self._edges: List[GridEdge] = [
            # Generation to Substation links
            GridEdge(
                id="line-gas-to-north",
                source="gen-gas-1",
                target="sub-north-1",
                capacity_mw=400.0,
                power_flow_mw=220.0,
                utilization_percent=55.0,
                status=EdgeStatus.NORMAL,
                risk_score=0.10,
                resistance_ohms=0.035,
                reactance_ohms=0.180,
            ),
            GridEdge(
                id="line-solar-to-north",
                source="gen-solar-1",
                target="sub-north-1",
                capacity_mw=250.0,
                power_flow_mw=140.0,
                utilization_percent=56.0,
                status=EdgeStatus.NORMAL,
                risk_score=0.12,
                resistance_ohms=0.040,
                reactance_ohms=0.200,
            ),
            GridEdge(
                id="line-wind-to-central",
                source="gen-wind-1",
                target="sub-central-1",
                capacity_mw=220.0,
                power_flow_mw=95.0,
                utilization_percent=43.18,
                status=EdgeStatus.NORMAL,
                risk_score=0.14,
                resistance_ohms=0.045,
                reactance_ohms=0.220,
            ),
            GridEdge(
                id="line-bess-to-north",
                source="bat-bess-1",
                target="sub-north-1",
                capacity_mw=120.0,
                power_flow_mw=20.0,
                utilization_percent=16.67,
                status=EdgeStatus.NORMAL,
                risk_score=0.08,
                resistance_ohms=0.025,
                reactance_ohms=0.120,
            ),
            # Inter-substation Transmission Backbone
            GridEdge(
                id="line-north-central-1",
                source="sub-north-1",
                target="sub-central-1",
                capacity_mw=500.0,
                power_flow_mw=340.0,
                utilization_percent=68.0,
                status=EdgeStatus.NORMAL,
                risk_score=0.22,
                resistance_ohms=0.020,
                reactance_ohms=0.095,
            ),
            GridEdge(
                id="line-central-south-1",
                source="sub-central-1",
                target="sub-south-1",
                capacity_mw=450.0,
                power_flow_mw=280.0,
                utilization_percent=62.22,
                status=EdgeStatus.NORMAL,
                risk_score=0.18,
                resistance_ohms=0.022,
                reactance_ohms=0.105,
            ),
            # Substation to Load Distribution links
            GridEdge(
                id="line-central-to-industrial",
                source="sub-central-1",
                target="load-industrial-1",
                capacity_mw=250.0,
                power_flow_mw=180.0,
                utilization_percent=72.0,
                status=EdgeStatus.NORMAL,
                risk_score=0.15,
                resistance_ohms=0.030,
                reactance_ohms=0.150,
            ),
            GridEdge(
                id="line-north-to-residential",
                source="sub-north-1",
                target="load-residential-1",
                capacity_mw=200.0,
                power_flow_mw=150.0,
                utilization_percent=75.0,
                status=EdgeStatus.NORMAL,
                risk_score=0.12,
                resistance_ohms=0.032,
                reactance_ohms=0.160,
            ),
            GridEdge(
                id="line-central-to-commercial",
                source="sub-central-1",
                target="load-commercial-1",
                capacity_mw=150.0,
                power_flow_mw=85.0,
                utilization_percent=56.67,
                status=EdgeStatus.NORMAL,
                risk_score=0.11,
                resistance_ohms=0.028,
                reactance_ohms=0.140,
            ),
            GridEdge(
                id="line-south-to-hospital",
                source="sub-south-1",
                target="load-hospital-metro",
                capacity_mw=100.0,
                power_flow_mw=45.0,
                utilization_percent=45.0,
                status=EdgeStatus.NORMAL,
                risk_score=0.06,
                resistance_ohms=0.018,
                reactance_ohms=0.090,
            ),
        ]

    def get_grid_state(self) -> GridResponse:
        """Calculates and returns the complete current grid state with summary metrics."""
        total_generation = 0.0
        renewable_generation = 0.0
        total_demand = 0.0

        for node in self._nodes:
            if node.type in (NodeType.CONVENTIONAL_GENERATOR, NodeType.SOLAR_PLANT, NodeType.WIND_PLANT):
                if node.status == NodeStatus.ONLINE:
                    total_generation += node.current_output_mw
                    if node.type in (NodeType.SOLAR_PLANT, NodeType.WIND_PLANT):
                        renewable_generation += node.current_output_mw
            elif node.type == NodeType.BATTERY:
                if node.status == NodeStatus.ONLINE and node.current_output_mw > 0:
                    total_generation += node.current_output_mw
            elif node.type in (NodeType.LOAD, NodeType.CRITICAL_LOAD):
                if node.status == NodeStatus.ONLINE:
                    total_demand += node.current_output_mw

        renewable_percentage = (
            round((renewable_generation / total_generation) * 100, 2)
            if total_generation > 0
            else 0.0
        )

        battery_node = next((n for n in self._nodes if n.type == NodeType.BATTERY), None)
        battery_soc = (
            battery_node.metadata.get("state_of_charge_percent", 78.5)
            if battery_node
            else 0.0
        )

        active_contingencies = sum(1 for e in self._edges if e.status != EdgeStatus.NORMAL) + sum(
            1 for n in self._nodes if n.status != NodeStatus.ONLINE
        )
        grid_risk_index = round(0.14 + (0.15 * active_contingencies), 4)

        summary = GridSummary(
            total_generation_mw=round(total_generation, 2),
            total_demand_mw=round(total_demand, 2),
            renewable_percentage=renewable_percentage,
            battery_soc=battery_soc,
            grid_risk_index=min(1.0, grid_risk_index),
            active_contingencies_count=active_contingencies,
            net_power_balance_mw=round(total_generation - total_demand, 2),
        )

        return GridResponse(
            nodes=self._nodes,
            edges=self._edges,
            summary=summary,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def get_all_component_ids(self) -> Set[str]:
        """Returns the set of all valid node and edge identifiers."""
        node_ids = {node.id for node in self._nodes}
        edge_ids = {edge.id for edge in self._edges}
        return node_ids.union(edge_ids)

    def component_exists(self, component_id: str) -> bool:
        """Validates whether a component exists in the grid topology."""
        return component_id in self.get_all_component_ids()

    def get_node_by_id(self, node_id: str) -> Optional[GridNode]:
        """Retrieves a specific node by ID."""
        for node in self._nodes:
            if node.id == node_id:
                return node
        return None

    def get_edge_by_id(self, edge_id: str) -> Optional[GridEdge]:
        """Retrieves a specific transmission edge by ID."""
        for edge in self._edges:
            if edge.id == edge_id:
                return edge
        return None


grid_service = GridService()
