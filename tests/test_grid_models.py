"""
Unit tests for PULSEiQ Grid Data Models and Mock Grid.
"""

import pytest
from ai.models.grid import (
    ComponentStatus,
    CriticalityLevel,
    ElectricityGrid,
    GridNode,
    NodeType,
    OperationalData,
    RiskMetrics,
    ScenarioConfig,
    TransmissionLine,
)
from ai.models.mock_grid import create_mock_grid


def test_grid_node_properties():
    """Verify GridNode initialization and status/classification properties."""
    node = GridNode(
        id="solar_test",
        name="Test Solar Farm",
        node_type=NodeType.SOLAR,
        status=ComponentStatus.ONLINE,
        operational=OperationalData(
            generation_mw=20.0,
            demand_mw=0.0,
            renewable_generation_mw=20.0,
            max_capacity_mw=25.0,
        ),
        risk=RiskMetrics(
            criticality=CriticalityLevel.MEDIUM,
            failure_probability=0.02,
        ),
    )

    assert node.id == "solar_test"
    assert node.is_operational is True
    assert node.is_renewable is True
    assert node.is_critical is False
    assert node.operational.net_power_mw == 20.0

    # Test critical node
    hosp_node = GridNode(
        id="hosp_test",
        name="County Hospital",
        node_type=NodeType.LOAD_CRITICAL,
        operational=OperationalData(demand_mw=5.0),
        risk=RiskMetrics(criticality=CriticalityLevel.CRITICAL),
    )
    assert hosp_node.is_critical is True
    assert hosp_node.is_renewable is False
    assert hosp_node.operational.net_power_mw == -5.0


def test_transmission_line_properties():
    """Verify TransmissionLine properties, utilization, and overload detection."""
    line = TransmissionLine(
        id="line_01",
        name="Line 1",
        source_node_id="gen_01",
        target_node_id="sub_01",
        capacity_mw=100.0,
        current_flow_mw=80.0,
        status=ComponentStatus.ONLINE,
    )

    assert line.utilization == 0.8
    assert line.utilization_pct == 80.0
    assert line.is_overloaded is False
    assert line.is_operational is True

    # Test overloaded line
    line.current_flow_mw = 110.0
    assert line.utilization == 1.1
    assert line.utilization_pct == 110.0
    assert line.is_overloaded is True

    # Test tripped line
    line.status = ComponentStatus.TRIPPED
    assert line.is_operational is False


def test_grid_serialization_roundtrip():
    """Verify ElectricityGrid serialization to and from dict / JSON."""
    grid = create_mock_grid("test_roundtrip_grid")
    grid_dict = grid.to_dict()
    grid_json = grid.to_json()

    # Reconstruct from dict
    restored_from_dict = ElectricityGrid.from_dict(grid_dict)
    assert restored_from_dict.grid_id == "test_roundtrip_grid"
    assert len(restored_from_dict.nodes) == len(grid.nodes)
    assert len(restored_from_dict.lines) == len(grid.lines)

    # Reconstruct from JSON
    restored_from_json = ElectricityGrid.from_json(grid_json)
    assert restored_from_json.grid_id == "test_roundtrip_grid"
    assert round(restored_from_json.total_generation_mw, 2) == round(grid.total_generation_mw, 2)
    assert round(restored_from_json.total_demand_mw, 2) == round(grid.total_demand_mw, 2)


def test_mock_grid_components_and_totals():
    """Verify that create_mock_grid contains all required node types and realistic values."""
    grid = create_mock_grid()

    # 1. Check all required component types exist
    node_types = {node.node_type for node in grid.nodes.values()}
    assert NodeType.GENERATOR in node_types
    assert NodeType.SOLAR in node_types
    assert NodeType.WIND in node_types
    assert NodeType.BATTERY in node_types
    assert NodeType.SUBSTATION in node_types
    assert NodeType.LOAD_NORMAL in node_types
    assert NodeType.LOAD_CRITICAL in node_types

    # 2. Check critical loads specifically (Hospital, Data center)
    critical_nodes = grid.get_nodes_by_type(NodeType.LOAD_CRITICAL)
    assert len(critical_nodes) >= 2
    hospital = grid.get_node("load_hospital_main")
    assert hospital is not None
    assert hospital.risk.criticality == CriticalityLevel.CRITICAL
    assert hospital.operational.demand_mw > 0

    # 3. Check renewable and total generation
    assert grid.total_generation_mw > 100.0  # Gas (75) + Solar (32) + Wind (28) = 135 MW
    assert grid.total_renewable_generation_mw == 60.0  # Solar (32) + Wind (28)
    assert grid.total_demand_mw > 100.0  # ~128.5 MW total demand
    assert grid.total_storage_capacity_mwh == 40.0

    # 4. Check validation produces zero topological errors
    errors = grid.validate_grid()
    assert len(errors) == 0, f"Mock grid validation failed: {errors}"


def test_scenario_application():
    """Verify scenario multiplier adjustments and contingency tripping."""
    grid = create_mock_grid()
    base_demand = grid.total_demand_mw
    base_gen = grid.total_generation_mw

    # Scenario: High peak demand (+20%), low solar (50%), trip gas generator
    scenario = ScenarioConfig(
        name="Heatwave with CCGT Outage",
        demand_multiplier=1.2,
        solar_multiplier=0.5,
        wind_multiplier=1.0,
        battery_availability=True,
        contingencies=["gen_gas_01", "line_submain_to_subnorth"],
    )

    stressed_grid = grid.apply_scenario(scenario)

    # Check original grid was not mutated
    assert grid.total_demand_mw == base_demand
    assert grid.get_node("gen_gas_01").status == ComponentStatus.ONLINE

    # Check stressed grid modifications
    assert stressed_grid.active_scenario.name == "Heatwave with CCGT Outage"
    assert stressed_grid.get_node("gen_gas_01").status == ComponentStatus.TRIPPED
    assert stressed_grid.get_node("gen_gas_01").operational.generation_mw == 0.0
    assert stressed_grid.get_line("line_submain_to_subnorth").status == ComponentStatus.TRIPPED

    # Demand increased by 20%
    assert round(stressed_grid.total_demand_mw, 2) == round(base_demand * 1.2, 2)

    # Solar generation halved (32 * 0.5 = 16 MW)
    solar_node = stressed_grid.get_node("solar_farm_01")
    assert solar_node.operational.generation_mw == 16.0
