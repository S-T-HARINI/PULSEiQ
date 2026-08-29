"""
PULSEiQ - NetworkX Graph Builder & Topology Analysis Engine.
Converts the ElectricityGrid data model into NetworkX graphs,
supporting dynamic node/edge mutations, cut-point/bridge discovery,
centrality calculations, and structured graph analysis outputs.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import networkx as nx

from ai.graph.models import GraphAnalysisResult
from ai.models.grid import ComponentStatus, ElectricityGrid, GridNode, NodeType, TransmissionLine


def grid_to_networkx(
    grid: ElectricityGrid,
    directed: bool = False,
    active_only: bool = False,
) -> nx.Graph:
    """
    Converts an ElectricityGrid object into a NetworkX graph (nx.Graph or nx.DiGraph).

    Args:
        grid: The ElectricityGrid instance containing nodes and lines.
        directed: If True, returns nx.DiGraph; otherwise undirected nx.Graph.
        active_only: If True, includes only nodes and lines with operational status.

    Returns:
        nx.Graph or nx.DiGraph populated with electrical and risk attributes.
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Cannot construct graph from an empty or None ElectricityGrid.")

    graph = nx.DiGraph() if directed else nx.Graph()

    graph.graph["grid_id"] = grid.grid_id
    graph.graph["name"] = grid.name
    graph.graph["description"] = grid.description

    # Add Nodes
    for node_id, node in grid.nodes.items():
        if active_only and not node.is_operational:
            continue
        add_grid_node(graph, node)

    # Add Edges
    for line_id, line in grid.lines.items():
        if active_only and not line.is_operational:
            continue
        add_transmission_edge(graph, line)

    return graph


def add_grid_node(graph: nx.Graph, node: GridNode) -> None:
    """Add a grid node and its associated attributes into a NetworkX graph."""
    if node is None:
        raise ValueError("Cannot add None node to graph.")

    graph.add_node(
        node.id,
        id=node.id,
        label=node.name,
        node_type=node.node_type.value,
        status=node.status.value,
        is_operational=node.is_operational,
        is_renewable=node.is_renewable,
        is_critical=node.is_critical,
        generation_mw=node.operational.generation_mw,
        demand_mw=node.operational.demand_mw,
        renewable_generation_mw=node.operational.renewable_generation_mw,
        net_power_mw=node.operational.net_power_mw,
        voltage_kv=node.operational.voltage_kv,
        voltage_pu=node.operational.voltage_pu,
        battery_soc_pct=node.operational.battery_soc_pct,
        battery_capacity_mwh=node.operational.battery_capacity_mwh,
        criticality=node.risk.criticality.value,
        failure_probability=node.risk.failure_probability,
        risk_score=node.risk.risk_score,
        vulnerability_factor=node.risk.vulnerability_factor,
        location=node.location,
        tags=node.tags,
    )


def add_transmission_edge(graph: nx.Graph, line: TransmissionLine) -> None:
    """Add a transmission line edge into a NetworkX graph."""
    if line is None:
        raise ValueError("Cannot add None transmission line to graph.")

    if line.source_node_id not in graph or line.target_node_id not in graph:
        return

    impedance_weight = max(line.reactance_ohm, 0.001)

    graph.add_edge(
        line.source_node_id,
        line.target_node_id,
        key=line.id,
        line_id=line.id,
        label=line.name,
        capacity_mw=line.capacity_mw,
        current_flow_mw=line.current_flow_mw,
        utilization_pct=line.utilization_pct,
        is_overloaded=line.is_overloaded,
        status=line.status.value,
        is_operational=line.is_operational,
        resistance_ohm=line.resistance_ohm,
        reactance_ohm=line.reactance_ohm,
        voltage_level_kv=line.voltage_level_kv,
        criticality=line.risk.criticality.value,
        failure_probability=line.risk.failure_probability,
        risk_score=line.risk.risk_score,
        weight=impedance_weight,
    )


def remove_failed_line(graph: nx.Graph, line_id: str) -> bool:
    """
    Finds and removes an edge corresponding to a failed transmission line ID.
    Returns True if found and removed.
    """
    edges_to_remove = []
    for u, v, data in graph.edges(data=True):
        if data.get("line_id") == line_id:
            edges_to_remove.append((u, v))

    for u, v in edges_to_remove:
        graph.remove_edge(u, v)

    return len(edges_to_remove) > 0


def remove_failed_node(graph: nx.Graph, node_id: str) -> bool:
    """Removes a failed node and all incident transmission lines from the graph."""
    if node_id in graph:
        graph.remove_node(node_id)
        return True
    return False


def find_connected_components(graph: nx.Graph) -> List[Set[str]]:
    """Returns list of connected component node sets (electrical islands)."""
    if graph.number_of_nodes() == 0:
        return []
    undirected = graph.to_undirected() if graph.is_directed() else graph
    return list(nx.connected_components(undirected))


def find_isolated_nodes(graph: nx.Graph) -> List[str]:
    """Identifies completely isolated buses with degree zero."""
    return list(nx.isolates(graph))


def find_isolated_load_nodes(graph: nx.Graph) -> List[str]:
    """
    Identifies load nodes that have lost all connections to generation sources.
    """
    if graph.number_of_nodes() == 0:
        return []

    undirected = graph.to_undirected() if graph.is_directed() else graph
    components = list(nx.connected_components(undirected))

    isolated_loads: List[str] = []

    for comp in components:
        has_generator = any(
            graph.nodes[nid].get("node_type") in (
                NodeType.GENERATOR.value,
                NodeType.SOLAR.value,
                NodeType.WIND.value,
                NodeType.BATTERY.value,
            )
            for nid in comp
        )
        if not has_generator:
            for nid in comp:
                if graph.nodes[nid].get("node_type") in (
                    NodeType.LOAD_NORMAL.value,
                    NodeType.LOAD_CRITICAL.value,
                ):
                    isolated_loads.append(nid)

    return isolated_loads


def identify_important_nodes(graph: nx.Graph, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Ranks nodes by composite structural importance (Degree Centrality + Betweenness Centrality + Criticality).
    """
    if graph.number_of_nodes() == 0:
        return []

    undirected = graph.to_undirected() if graph.is_directed() else graph
    deg_cent = nx.degree_centrality(undirected)
    bet_cent = nx.betweenness_centrality(undirected, weight="weight")
    close_cent = nx.closeness_centrality(undirected)

    ranked = []
    for nid, node_data in graph.nodes(data=True):
        dc = deg_cent.get(nid, 0.0)
        bc = bet_cent.get(nid, 0.0)
        cc = close_cent.get(nid, 0.0)
        is_crit = node_data.get("is_critical", False)
        crit_boost = 0.30 if is_crit else 0.0

        composite_score = (dc * 0.35) + (bc * 0.35) + (cc * 0.10) + crit_boost

        ranked.append({
            "node_id": nid,
            "name": node_data.get("label", nid),
            "node_type": node_data.get("node_type", "unknown"),
            "degree": undirected.degree(nid),
            "degree_centrality": round(dc, 4),
            "betweenness_centrality": round(bc, 4),
            "closeness_centrality": round(cc, 4),
            "is_critical": is_crit,
            "importance_score": round(composite_score, 4),
        })

    ranked.sort(key=lambda x: x["importance_score"], reverse=True)
    return ranked[:top_n]


def find_shortest_path(
    graph: nx.Graph,
    source: str,
    target: str,
    weight: str = "weight",
) -> Optional[List[str]]:
    """Finds lowest-impedance path between two grid nodes."""
    try:
        return nx.shortest_path(graph, source=source, target=target, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def get_topology_summary(graph: nx.Graph) -> Dict[str, Any]:
    """Computes topological properties for a grid graph."""
    undirected = graph.to_undirected() if graph.is_directed() else graph
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()

    if node_count == 0:
        return {
            "node_count": 0,
            "edge_count": 0,
            "is_connected": False,
            "connected_components_count": 0,
            "density": 0.0,
            "average_degree": 0.0,
            "isolated_nodes": [],
        }

    is_connected = nx.is_connected(undirected)
    connected_components = list(nx.connected_components(undirected))
    density = nx.density(graph)
    degrees = dict(graph.degree())
    avg_degree = sum(degrees.values()) / max(node_count, 1)
    isolated = list(nx.isolates(graph))

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "is_connected": is_connected,
        "connected_components_count": len(connected_components),
        "density": round(density, 4),
        "average_degree": round(avg_degree, 2),
        "isolated_nodes": isolated,
    }


def calculate_node_degrees(graph: nx.Graph) -> Dict[str, int]:
    """Returns mapping of node ID to degree."""
    return dict(graph.degree())


def calculate_degree_centrality(graph: nx.Graph) -> Dict[str, float]:
    """Calculates degree centrality for all nodes."""
    return nx.degree_centrality(graph)


def calculate_betweenness_centrality(graph: nx.Graph) -> Dict[str, float]:
    """Calculates betweenness centrality for all nodes."""
    return nx.betweenness_centrality(graph, weight="weight")


def calculate_closeness_centrality(graph: nx.Graph) -> Dict[str, float]:
    """Calculates closeness centrality for all nodes."""
    return nx.closeness_centrality(graph)


def find_articulation_points(graph: nx.Graph) -> List[str]:
    """Finds cut vertices (nodes whose removal splits the graph)."""
    if graph.number_of_nodes() == 0:
        return []
    undirected = graph.to_undirected() if graph.is_directed() else graph
    return list(nx.articulation_points(undirected))


def find_bridges(graph: nx.Graph) -> List[Tuple[str, str]]:
    """Finds bridge edges (lines whose removal splits the graph)."""
    if graph.number_of_nodes() == 0:
        return []
    undirected = graph.to_undirected() if graph.is_directed() else graph
    return list(nx.bridges(undirected))


def analyze_graph_topology(
    graph: nx.Graph,
    grid: Optional[ElectricityGrid] = None,
) -> GraphAnalysisResult:
    """
    Executes full structured topological analysis on an electricity grid graph.

    Args:
        graph: NetworkX graph representing the electricity grid.
        grid: (Optional) ElectricityGrid object for enrichment.

    Returns:
        GraphAnalysisResult structured dataclass.
    """
    grid_id = graph.graph.get("grid_id", "unknown_grid")
    summary = get_topology_summary(graph)

    deg_cent = calculate_degree_centrality(graph)
    bet_cent = calculate_betweenness_centrality(graph)
    close_cent = calculate_closeness_centrality(graph)
    articulation_pts = find_articulation_points(graph)
    bridges = find_bridges(graph)
    isolated_loads = find_isolated_load_nodes(graph)
    critical_hubs = identify_important_nodes(graph, top_n=5)

    # Identify vulnerable lines (bridges with high flow/capacity)
    vulnerable_lines = []
    for u, v in bridges:
        edge_data = graph.get_edge_data(u, v) or {}
        line_id = edge_data.get("line_id", f"{u}--{v}")
        vulnerable_lines.append({
            "line_id": line_id,
            "source_node_id": u,
            "target_node_id": v,
            "capacity_mw": edge_data.get("capacity_mw", 0.0),
            "current_flow_mw": edge_data.get("current_flow_mw", 0.0),
            "utilization_pct": edge_data.get("utilization_pct", 0.0),
            "is_bridge": True,
            "description": f"Bridge line between {u} and {v}: loss causes immediate network islanding",
        })

    return GraphAnalysisResult(
        grid_id=grid_id,
        node_count=summary["node_count"],
        edge_count=summary["edge_count"],
        is_connected=summary["is_connected"],
        connected_components_count=summary["connected_components_count"],
        density=summary["density"],
        average_degree=summary["average_degree"],
        degrees=dict(graph.degree()),
        degree_centrality=deg_cent,
        betweenness_centrality=bet_cent,
        closeness_centrality=close_cent,
        articulation_points=articulation_pts,
        bridges=bridges,
        isolated_nodes=summary["isolated_nodes"],
        isolated_load_nodes=isolated_loads,
        critical_hubs=critical_hubs,
        vulnerable_lines=vulnerable_lines,
        summary={
            "is_single_component": summary["is_connected"],
            "articulation_points_count": len(articulation_pts),
            "bridges_count": len(bridges),
            "isolated_loads_count": len(isolated_loads),
        },
    )


def export_graph_to_dict(graph: nx.Graph, edges_key: str = "links") -> Dict[str, Any]:
    """Serialize graph to node-link dictionary format."""
    try:
        return nx.node_link_data(graph, edges=edges_key)
    except TypeError:
        return nx.node_link_data(graph)
