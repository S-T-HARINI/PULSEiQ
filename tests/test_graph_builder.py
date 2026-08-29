"""
Unit tests for NetworkX Graph Builder & Topology Utilities.
"""

import pytest
import networkx as nx

from ai.models.grid import ComponentStatus, CriticalityLevel, ElectricityGrid, NodeType
from ai.models.mock_grid import create_mock_grid
from ai.graph.builder import (
    add_grid_node,
    add_transmission_edge,
    analyze_graph_topology,
    calculate_betweenness_centrality,
    calculate_closeness_centrality,
    calculate_degree_centrality,
    calculate_node_degrees,
    export_graph_to_dict,
    find_articulation_points,
    find_bridges,
    find_connected_components,
    find_isolated_load_nodes,
    find_isolated_nodes,
    find_shortest_path,
    get_topology_summary,
    grid_to_networkx,
    identify_important_nodes,
    remove_failed_line,
    remove_failed_node,
)


def test_grid_to_networkx_conversion():
    """Verify conversion of ElectricityGrid to NetworkX Graph with attributes."""
    grid = create_mock_grid()
    graph = grid_to_networkx(grid)

    assert isinstance(graph, nx.Graph)
    assert graph.number_of_nodes() == len(grid.nodes)
    assert graph.number_of_edges() == len(grid.lines)

    # Verify node attributes
    hospital_data = graph.nodes["load_hospital_main"]
    assert hospital_data["node_type"] == NodeType.LOAD_CRITICAL.value
    assert hospital_data["demand_mw"] == 8.5
    assert hospital_data["criticality"] == CriticalityLevel.CRITICAL.value
    assert hospital_data["is_critical"] is True

    # Verify edge attributes
    edge_data = graph.get_edge_data("gen_gas_01", "sub_trans_main")
    assert edge_data is not None
    assert edge_data["capacity_mw"] == 150.0
    assert edge_data["current_flow_mw"] == 75.0
    assert edge_data["utilization_pct"] == 50.0


def test_grid_to_networkx_directed():
    """Verify conversion to DiGraph."""
    grid = create_mock_grid()
    digraph = grid_to_networkx(grid, directed=True)

    assert isinstance(digraph, nx.DiGraph)
    assert digraph.has_edge("gen_gas_01", "sub_trans_main")


def test_topology_metrics():
    """Verify topological property extraction functions."""
    grid = create_mock_grid()
    graph = grid_to_networkx(grid)

    summary = get_topology_summary(graph)
    assert summary["node_count"] == 12
    assert summary["edge_count"] == 12
    assert summary["is_connected"] is True
    assert summary["connected_components_count"] == 1
    assert summary["density"] > 0.0
    assert summary["average_degree"] == 2.0
    assert len(summary["isolated_nodes"]) == 0

    degrees = calculate_node_degrees(graph)
    assert degrees["sub_trans_main"] >= 5

    deg_centrality = calculate_degree_centrality(graph)
    assert "sub_trans_main" in deg_centrality
    assert deg_centrality["sub_trans_main"] == max(deg_centrality.values())

    bet_centrality = calculate_betweenness_centrality(graph)
    assert bet_centrality["sub_trans_main"] > 0

    close_centrality = calculate_closeness_centrality(graph)
    assert close_centrality["sub_trans_main"] > 0


def test_vulnerability_points():
    """Verify articulation points and bridge discovery."""
    grid = create_mock_grid()
    graph = grid_to_networkx(grid)

    articulation_pts = find_articulation_points(graph)
    bridges = find_bridges(graph)

    assert "sub_trans_main" in articulation_pts
    assert len(bridges) > 0


def test_dynamic_graph_mutations():
    """Verify dynamic node/line removal and islanding detection."""
    grid = create_mock_grid()
    graph = grid_to_networkx(grid)

    # Important node ranking
    important = identify_important_nodes(graph, top_n=3)
    assert len(important) == 3
    assert important[0]["node_id"] == "sub_trans_main"

    # Shortest path
    path = find_shortest_path(graph, "gen_gas_01", "load_hospital_main")
    assert path is not None
    assert path[0] == "gen_gas_01"
    assert path[-1] == "load_hospital_main"

    # Line removal
    removed = remove_failed_line(graph, "line_subnorth_to_hospital")
    assert removed is True
    assert "load_hospital_main" in find_isolated_nodes(graph)

    # Node removal
    removed_node = remove_failed_node(graph, "sub_trans_main")
    assert removed_node is True
    components = find_connected_components(graph)
    assert len(components) > 1


def test_analyze_graph_topology_structured():
    """Verify full structured topology analysis returning GraphAnalysisResult."""
    grid = create_mock_grid()
    graph = grid_to_networkx(grid)

    analysis = analyze_graph_topology(graph, grid=grid)
    assert analysis.grid_id == grid.grid_id
    assert analysis.node_count == 12
    assert analysis.edge_count == 12
    assert analysis.is_connected is True
    assert len(analysis.critical_hubs) <= 5
    assert len(analysis.vulnerable_lines) > 0

    # Test serialization
    data = analysis.to_dict()
    assert "node_count" in data
    assert "articulation_points" in data
    assert "bridges" in data
    assert "degree_centrality" in data


def test_graph_error_handling():
    """Verify graph builder error handling."""
    empty_grid = ElectricityGrid(grid_id="empty", name="Empty")
    with pytest.raises(ValueError, match="Cannot construct graph from an empty"):
        grid_to_networkx(empty_grid)

    # Test add None node
    G = nx.Graph()
    with pytest.raises(ValueError, match="Cannot add None node"):
        add_grid_node(G, None)

    # Test add None line
    with pytest.raises(ValueError, match="Cannot add None transmission line"):
        add_transmission_edge(G, None)
