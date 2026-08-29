"""
PULSEiQ - Grid Risk & Contingency Assessment Engine.
Implements N-1 screening, N-k multi-contingency evaluation, sequential cascading failure simulation,
critical component ranking, and standardized multi-factor grid risk scoring.
"""

from itertools import combinations
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx
import numpy as np

from ai.graph.builder import (
    calculate_betweenness_centrality,
    calculate_degree_centrality,
    find_articulation_points,
    find_bridges,
    find_connected_components,
    find_isolated_load_nodes,
    find_isolated_nodes,
    grid_to_networkx,
)
from ai.models.grid import (
    ComponentStatus,
    CriticalityLevel,
    ElectricityGrid,
    GridNode,
    NodeType,
    ScenarioConfig,
    TransmissionLine,
)
from ai.risk.models import (
    CascadingFailureReport,
    CascadingStage,
    ComponentCriticality,
    ConnectivitySummary,
    ContingencyResult,
    ContingencyType,
    GridRiskAssessment,
    RiskLevel,
    RiskThresholds,
    RiskWeightsConfig,
)
from ai.simulation.power_flow import solve_power_flow


def analyze_n_k(
    grid: ElectricityGrid,
    failed_components: List[str],
    contingency_type: ContingencyType = ContingencyType.N_MINUS_K,
    contingency_id: Optional[str] = None,
) -> ContingencyResult:
    """
    Evaluates power flow, topological connectivity, line overloads, and critical-load exposure
    under an arbitrary set of failed components (lines, generators, substations).

    Args:
        grid: The ElectricityGrid model.
        failed_components: List of component IDs to trip/fail.
        contingency_type: Category of contingency (N-1 line, N-1 gen, N-k, etc.).
        contingency_id: (Optional) Identifier string for the contingency.

    Returns:
        ContingencyResult structured dataclass.

    Raises:
        ValueError: If grid is empty or failed_components contains invalid IDs.
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Grid is empty or None.")

    valid_ids = set(grid.nodes.keys()).union(grid.lines.keys())
    for comp_id in failed_components:
        if comp_id not in valid_ids:
            raise ValueError(f"Unknown failed component ID '{comp_id}' not present in grid.")

    if contingency_id is None:
        prefix = "N-1" if len(failed_components) == 1 else f"N-{len(failed_components)}"
        contingency_id = f"{prefix}_{'_'.join(failed_components)}"

    # 1. Apply Contingency Outages to Grid Deep Copy
    scenario = ScenarioConfig(
        name=f"Contingency_{contingency_id}",
        contingencies=failed_components,
    )
    tripped_grid = grid.apply_scenario(scenario)

    # 2. Graph Topology & Connectivity Evaluation
    G = grid_to_networkx(tripped_grid, active_only=True)
    connected_comps = find_connected_components(G)
    isolated_nodes = find_isolated_nodes(G)
    isolated_loads = find_isolated_load_nodes(G)

    # Identify isolated critical loads
    isolated_critical_loads = [
        nid for nid in isolated_loads
        if nid in grid.nodes and grid.nodes[nid].is_critical
    ]
    for nid in failed_components:
        if nid in grid.nodes and grid.nodes[nid].is_critical:
            if nid not in isolated_critical_loads:
                isolated_critical_loads.append(nid)

    connectivity_summary = ConnectivitySummary(
        is_connected=len(connected_comps) <= 1 and len(isolated_nodes) == 0,
        connected_components_count=len(connected_comps),
        isolated_nodes=isolated_nodes,
        isolated_critical_loads=isolated_critical_loads,
    )

    # 3. Solve Power Flow on Post-Contingency Grid
    sim_res = solve_power_flow(tripped_grid)

    overloaded_components = []
    overloaded_line_ids = []
    for lid, lres in sim_res.line_results.items():
        if lres.is_overloaded and lid not in failed_components:
            overloaded_line_ids.append(lid)
            overloaded_components.append({
                "component_id": lid,
                "name": lres.line_name,
                "flow_mw": lres.flow_mw,
                "capacity_mw": lres.capacity_mw,
                "utilization_pct": lres.utilization_pct,
            })

    # 4. Critical Load Impact & Unserved Demand
    critical_load_lost_mw = sum(
        grid.nodes[nid].operational.demand_mw
        for nid in isolated_critical_loads
        if nid in grid.nodes
    )
    critical_at_risk = len(isolated_critical_loads) > 0 or (
        sim_res.unserved_load_mw > 0.1 and sim_res.power_imbalance_mw < -0.1
    )

    unserved_total_mw = sim_res.unserved_load_mw + critical_load_lost_mw

    # 5. Operational & Security Status
    is_secure = (
        len(overloaded_line_ids) == 0
        and unserved_total_mw <= 0.1
        and sim_res.is_frequency_stable
        and not critical_at_risk
        and connectivity_summary.is_connected
    )
    is_grid_operational = (
        unserved_total_mw < 0.85 * max(grid.total_demand_mw, 1.0)
        and sim_res.is_frequency_stable
    )

    # 6. Severity & Risk Score Calculation (0 to 100)
    overload_penalty = len(overloaded_line_ids) * 15.0 + max(0.0, sim_res.max_line_utilization_pct - 100.0) * 0.5
    loss_of_load_penalty = (unserved_total_mw / max(grid.total_demand_mw, 1.0)) * 50.0
    critical_penalty = 30.0 if critical_at_risk else 0.0
    freq_penalty = 15.0 if not sim_res.is_frequency_stable else 0.0
    island_penalty = max(0, len(connected_comps) - 1) * 10.0

    severity_score = min(100.0, overload_penalty + loss_of_load_penalty + critical_penalty + freq_penalty + island_penalty)

    # Categorical severity
    if severity_score < 25.0:
        severity_level = "LOW"
    elif severity_score < 50.0:
        severity_level = "MODERATE"
    elif severity_score < 75.0:
        severity_level = "HIGH"
    else:
        severity_level = "CRITICAL"

    # Affected components (tripped + overloaded + isolated)
    affected_components = list(set(failed_components + overloaded_line_ids + isolated_nodes + isolated_loads))

    return ContingencyResult(
        contingency_id=contingency_id,
        tripped_components=failed_components,
        contingency_type=contingency_type,
        is_grid_operational=is_grid_operational,
        is_secure=is_secure,
        affected_components=affected_components,
        connectivity=connectivity_summary,
        overloaded_components=overloaded_components,
        unserved_load_mw=round(unserved_total_mw, 3),
        critical_load_affected_mw=round(critical_load_lost_mw, 3),
        critical_load_at_risk=critical_at_risk,
        max_line_utilization_pct=round(sim_res.max_line_utilization_pct, 2),
        frequency_hz=round(sim_res.frequency_hz, 4),
        risk_score=round(severity_score, 2),
        severity=severity_level,
    )


# Backward-compatible alias
def evaluate_contingency(
    grid: ElectricityGrid,
    contingency_id: str,
    tripped_ids: List[str],
    contingency_type: ContingencyType,
) -> ContingencyResult:
    return analyze_n_k(
        grid=grid,
        failed_components=tripped_ids,
        contingency_type=contingency_type,
        contingency_id=contingency_id,
    )


def run_n_1_analysis(
    grid: ElectricityGrid,
    top_n_worst: int = 10,
) -> List[ContingencyResult]:
    """
    Exhaustively evaluates all single-component outages:
    - Every operational transmission line (N-1 Line)
    - Every operational generator & renewable farm (N-1 Gen)
    - Every operational major battery and substation (N-1 Component)

    Returns results sorted by severity score descending.
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Grid is empty or None.")

    results: List[ContingencyResult] = []

    # 1. Test all operational transmission lines
    for line_id, line in grid.lines.items():
        if not line.is_operational:
            continue
        c_res = analyze_n_k(
            grid=grid,
            failed_components=[line_id],
            contingency_type=ContingencyType.N_MINUS_1_LINE,
            contingency_id=f"N-1_{line_id}",
        )
        results.append(c_res)

    # 2. Test all operational generation assets
    for node_id, node in grid.nodes.items():
        if not node.is_operational:
            continue

        if node.node_type in (NodeType.GENERATOR, NodeType.SOLAR, NodeType.WIND):
            c_type = ContingencyType.N_MINUS_1_GEN
        elif node.node_type in (NodeType.BATTERY, NodeType.SUBSTATION):
            c_type = ContingencyType.N_MINUS_1_COMPONENT
        else:
            continue

        c_res = analyze_n_k(
            grid=grid,
            failed_components=[node_id],
            contingency_type=c_type,
            contingency_id=f"N-1_{node_id}",
        )
        results.append(c_res)

    results.sort(key=lambda x: x.risk_score, reverse=True)
    return results[:top_n_worst] if top_n_worst > 0 else results


def run_n_k_analysis(
    grid: ElectricityGrid,
    k: int = 2,
    candidate_failures: Optional[List[str]] = None,
    max_combinations: int = 30,
) -> List[ContingencyResult]:
    """
    Evaluates high-impact multi-component N-k outages (k=2 by default).
    Prioritizes combinations of high-criticality assets and large capacity feeds.
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Grid is empty or None.")

    if candidate_failures is None:
        candidate_assets: List[Tuple[str, float]] = []

        # Prioritize critical lines and large generation assets
        for lid, line in grid.lines.items():
            weight = line.capacity_mw * (2.0 if line.risk.criticality == CriticalityLevel.CRITICAL else 1.0)
            candidate_assets.append((lid, weight))

        for nid, node in grid.nodes.items():
            if node.node_type in (NodeType.GENERATOR, NodeType.SOLAR, NodeType.WIND, NodeType.BATTERY, NodeType.SUBSTATION):
                weight = max(node.operational.max_capacity_mw, 20.0) * (2.0 if node.is_critical else 1.0)
                candidate_assets.append((nid, weight))

        candidate_assets.sort(key=lambda x: x[1], reverse=True)
        candidate_pool = [c[0] for c in candidate_assets[:12]]
    else:
        candidate_pool = list(candidate_failures)

    combos = list(combinations(candidate_pool, k))[:max_combinations]
    results: List[ContingencyResult] = []

    for combo in combos:
        c_id = f"N-{k}_{'_'.join(combo)}"
        c_res = analyze_n_k(
            grid=grid,
            failed_components=list(combo),
            contingency_type=ContingencyType.N_MINUS_K,
            contingency_id=c_id,
        )
        results.append(c_res)

    results.sort(key=lambda x: x.risk_score, reverse=True)
    return results


def simulate_cascading_failure(
    grid: ElectricityGrid,
    initial_trips: List[str],
    overload_threshold_pct: float = 115.0,
    max_stages: int = 8,
) -> CascadingFailureReport:
    """
    Simulates sequential cascading line outages triggered by thermal overloads.

    Stage 0: Initial component failures applied. Power flow solved.
    Stage 1..N: Any transmission lines exceeding overload_threshold_pct (e.g. 115%) trip.
                Power flow is re-solved, and the cascade propagates until the network stabilizes
                or collapses.
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Grid is empty or None.")

    valid_ids = set(grid.nodes.keys()).union(grid.lines.keys())
    for comp_id in initial_trips:
        if comp_id not in valid_ids:
            raise ValueError(f"Unknown initial trip ID '{comp_id}'.")

    current_trips = list(initial_trips)
    stages: List[CascadingStage] = []
    secondary_trips: List[str] = []

    for stage_idx in range(max_stages):
        scenario = ScenarioConfig(
            name=f"Cascade_Stage_{stage_idx}",
            contingencies=current_trips,
        )
        post_grid = grid.apply_scenario(scenario)
        sim_res = solve_power_flow(post_grid)

        # Detect newly overloaded operational lines exceeding thermal trip threshold
        new_overloaded = [
            lid for lid, lres in sim_res.line_results.items()
            if lres.utilization_pct >= overload_threshold_pct and lid not in current_trips
        ]

        # Calculate critical unserved MW in this stage
        critical_unserved = sum(
            n.operational.demand_mw for n in grid.nodes.values()
            if n.is_critical and (n.id in current_trips or sim_res.unserved_load_mw > 5.0)
        )

        is_stable = len(new_overloaded) == 0

        stage_record = CascadingStage(
            stage_index=stage_idx + 1,
            tripped_in_this_stage=new_overloaded if stage_idx > 0 else list(initial_trips),
            overloaded_lines_detected=[
                lid for lid, lres in sim_res.line_results.items() if lres.is_overloaded
            ],
            unserved_load_mw=sim_res.unserved_load_mw,
            critical_unserved_mw=critical_unserved,
            system_frequency_hz=sim_res.frequency_hz,
            is_stable=is_stable,
        )
        stages.append(stage_record)

        if is_stable:
            break

        secondary_trips.extend(new_overloaded)
        current_trips.extend(new_overloaded)

    # Final State Assessment
    final_grid = grid.apply_scenario(ScenarioConfig(contingencies=current_trips))
    final_sim = solve_power_flow(final_grid)
    final_unserved = final_sim.unserved_load_mw
    total_lines_lost = sum(1 for cid in current_trips if cid in grid.lines)
    blackout = final_unserved >= 0.80 * grid.total_demand_mw

    cascade_score = min(
        100.0,
        (len(stages) * 12.0)
        + (total_lines_lost * 8.0)
        + (final_unserved / max(grid.total_demand_mw, 1.0)) * 50.0,
    )

    final_state = {
        "is_stable": stages[-1].is_stable if stages else True,
        "blackout_occurred": blackout,
        "total_unserved_mw": round(final_unserved, 3),
        "total_lines_lost": total_lines_lost,
        "final_frequency_hz": round(final_sim.frequency_hz, 4),
        "max_line_utilization_pct": round(final_sim.max_line_utilization_pct, 2),
    }

    return CascadingFailureReport(
        initiating_contingency=initial_trips,
        total_stages=len(stages),
        stages=stages,
        initial_failure=list(initial_trips),
        secondary_failures=secondary_trips,
        final_state=final_state,
        final_unserved_mw=round(final_unserved, 3),
        final_critical_unserved_mw=round(stages[-1].critical_unserved_mw if stages else 0.0, 3),
        blackout_occurred=blackout,
        total_lines_lost=total_lines_lost,
        cascade_risk_score=round(cascade_score, 2),
    )


def rank_critical_components(
    grid: ElectricityGrid,
    graph: Optional[nx.Graph] = None,
    top_n: int = 10,
) -> List[ComponentCriticality]:
    """
    Ranks grid components dynamically by vulnerability and operational criticality.

    Considers:
    - Structural Centrality (Betweenness & Degree Centrality in NetworkX)
    - Current Component Utilization (%)
    - Critical Load Exposure (MW of critical hospital/datacenter loads reliant on this node/line)
    - Component Failure Probability & Risk Rating
    - Articulation Point (cut-vertex) or Bridge (cut-edge) status
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Grid is empty or None.")

    if graph is None:
        graph = grid_to_networkx(grid)

    deg_cent = calculate_degree_centrality(graph)
    bet_cent = calculate_betweenness_centrality(graph)
    articulation_pts = set(find_articulation_points(graph))
    bridges = set(find_bridges(graph))

    # Precalculate critical loads
    critical_load_nodes = [n for n in grid.nodes.values() if n.is_critical]
    total_critical_mw = sum(n.operational.demand_mw for n in critical_load_nodes)

    ranked_list: List[ComponentCriticality] = []

    # 1. Rank Nodes
    for nid, node in grid.nodes.items():
        dc = deg_cent.get(nid, 0.0)
        bc = bet_cent.get(nid, 0.0)
        centrality = (dc * 0.40) + (bc * 0.60)

        is_art = nid in articulation_pts
        is_crit = node.is_critical or node.risk.criticality == CriticalityLevel.CRITICAL

        # Utilization
        if node.node_type in (NodeType.GENERATOR, NodeType.SOLAR, NodeType.WIND, NodeType.BATTERY):
            cap = max(node.operational.max_capacity_mw, 0.1)
            utilization = (node.operational.generation_mw / cap) * 100.0
        elif node.node_type in (NodeType.LOAD_NORMAL, NodeType.LOAD_CRITICAL):
            cap = max(node.operational.max_capacity_mw, node.operational.demand_mw, 0.1)
            utilization = (node.operational.demand_mw / cap) * 100.0
        else:
            utilization = 50.0

        # Critical Load Exposure: check if critical loads disconnect if this node fails
        G_temp = graph.copy()
        if nid in G_temp:
            G_temp.remove_node(nid)
        isolated_loads = find_isolated_load_nodes(G_temp)
        critical_exposure_mw = sum(
            grid.nodes[i_id].operational.demand_mw
            for i_id in isolated_loads
            if i_id in grid.nodes and grid.nodes[i_id].is_critical
        )
        if node.is_critical:
            critical_exposure_mw += node.operational.demand_mw

        # Composite Criticality Score (0 to 100)
        art_boost = 25.0 if is_art else 0.0
        crit_boost = 30.0 if is_crit else 0.0
        exposure_factor = (critical_exposure_mw / max(total_critical_mw, 1.0)) * 25.0
        cent_factor = centrality * 20.0
        util_factor = (min(utilization, 100.0) / 100.0) * 15.0
        p_fail_factor = min(node.risk.failure_probability * 500.0, 10.0)

        risk_score = min(100.0, art_boost + crit_boost + exposure_factor + cent_factor + util_factor + p_fail_factor)

        ranked_list.append(
            ComponentCriticality(
                component_id=node.id,
                component_name=node.name,
                component_type=node.node_type.value,
                risk_score=round(risk_score, 2),
                centrality_score=round(centrality, 4),
                utilization_pct=round(utilization, 2),
                critical_load_exposure_mw=round(critical_exposure_mw, 3),
                is_critical=is_crit,
                is_articulation_point=is_art,
                is_bridge=False,
                metadata={"nominal_voltage_kv": node.operational.voltage_kv},
            )
        )

    # 2. Rank Transmission Lines
    for lid, line in grid.lines.items():
        is_bridge = (line.source_node_id, line.target_node_id) in bridges or (line.target_node_id, line.source_node_id) in bridges
        is_crit = line.risk.criticality in (CriticalityLevel.HIGH, CriticalityLevel.CRITICAL)

        # Approximate line centrality as average of endpoints
        dc_avg = (deg_cent.get(line.source_node_id, 0.0) + deg_cent.get(line.target_node_id, 0.0)) / 2.0
        bc_avg = (bet_cent.get(line.source_node_id, 0.0) + bet_cent.get(line.target_node_id, 0.0)) / 2.0
        centrality = (dc_avg * 0.40) + (bc_avg * 0.60)

        # Critical Load Exposure if line fails
        G_temp = graph.copy()
        for u, v, data in list(G_temp.edges(data=True)):
            if data.get("line_id") == lid:
                G_temp.remove_edge(u, v)

        isolated_loads = find_isolated_load_nodes(G_temp)
        critical_exposure_mw = sum(
            grid.nodes[i_id].operational.demand_mw
            for i_id in isolated_loads
            if i_id in grid.nodes and grid.nodes[i_id].is_critical
        )

        bridge_boost = 25.0 if is_bridge else 0.0
        crit_boost = 20.0 if is_crit else 0.0
        exposure_factor = (critical_exposure_mw / max(total_critical_mw, 1.0)) * 25.0
        util_factor = (min(line.utilization_pct, 120.0) / 100.0) * 20.0
        cent_factor = centrality * 15.0

        risk_score = min(100.0, bridge_boost + crit_boost + exposure_factor + util_factor + cent_factor)

        ranked_list.append(
            ComponentCriticality(
                component_id=line.id,
                component_name=line.name,
                component_type="transmission_line",
                risk_score=round(risk_score, 2),
                centrality_score=round(centrality, 4),
                utilization_pct=round(line.utilization_pct, 2),
                critical_load_exposure_mw=round(critical_exposure_mw, 3),
                is_critical=is_crit,
                is_articulation_point=False,
                is_bridge=is_bridge,
                metadata={"capacity_mw": line.capacity_mw, "voltage_kv": line.voltage_level_kv},
            )
        )

    # Sort descending by risk score
    ranked_list.sort(key=lambda x: x.risk_score, reverse=True)
    for rank_idx, comp in enumerate(ranked_list, start=1):
        comp.overall_criticality_rank = rank_idx

    return ranked_list[:top_n] if top_n > 0 else ranked_list


def calculate_grid_risk_index(
    grid: ElectricityGrid,
    config: Optional[RiskWeightsConfig] = None,
) -> GridRiskAssessment:
    """
    Computes standard overall grid risk scorecard for PULSEiQ.
    Outputs structured summary matching FastAPI contract specifications.

    Risk Scale:
      0.00 - 0.25: LOW
      0.25 - 0.50: MODERATE
      0.50 - 0.75: HIGH
      0.75 - 1.00: CRITICAL
    """
    if grid is None or len(grid.nodes) == 0:
        raise ValueError("Cannot calculate risk index on an empty or None grid.")

    if config is None:
        config = RiskWeightsConfig()

    n1_results = run_n_1_analysis(grid, top_n_worst=15)
    n1_violations = [c for c in n1_results if not c.is_secure]

    # Baseline power flow
    base_sim = solve_power_flow(grid)

    failed_components = [
        nid for nid, n in grid.nodes.items() if not n.is_operational
    ] + [
        lid for lid, l in grid.lines.items() if not l.is_operational
    ]

    G = grid_to_networkx(grid)
    ranked_components = rank_critical_components(grid, graph=G, top_n=5)

    # 1. Multi-factor calculation
    # Factor A: N-1 Insecurity
    n1_insecurity_factor = len(n1_violations) / max(len(n1_results), 1)

    # Factor B: Line Loading & Overload Risk
    loading_factor = min(1.0, base_sim.max_line_utilization_pct / 100.0)

    # Factor C: Critical Load Exposure
    critical_loads = [n for n in grid.nodes.values() if n.is_critical]
    total_critical_mw = sum(n.operational.demand_mw for n in critical_loads)
    critical_at_risk = any(c.critical_load_at_risk for c in n1_violations) or base_sim.unserved_load_mw > 0.1
    critical_exposure_factor = 1.0 if critical_at_risk else 0.0

    # Factor D: Generation Reserve Margin (Deficit = High Risk)
    reserve_mw = grid.total_generation_mw - grid.total_demand_mw
    reserve_ratio = reserve_mw / max(grid.total_demand_mw, 1.0)
    # Target reserve is +15%; below 0 is high risk
    reserve_risk_factor = float(np.clip(1.0 - (reserve_ratio / 0.15), 0.0, 1.0))

    # Factor E: Renewable Intermittency Variability
    total_ren = grid.total_renewable_generation_mw
    renewable_penetration = total_ren / max(grid.total_generation_mw, 1.0)
    renewable_variability_factor = min(1.0, renewable_penetration * 0.8)

    # Factor F: Battery Storage Margin
    bess_nodes = [n for n in grid.nodes.values() if n.node_type == NodeType.BATTERY]
    if bess_nodes:
        avg_soc = sum(b.operational.battery_soc_pct for b in bess_nodes) / len(bess_nodes)
        battery_risk_factor = float(np.clip(1.0 - (avg_soc / 100.0), 0.0, 1.0))
    else:
        battery_risk_factor = 0.50

    # Factor G: Voltage & Frequency Deviations
    freq_dev = abs(base_sim.frequency_hz - 60.0)
    voltage_dev_factor = min(1.0, (freq_dev / 0.50) + (base_sim.risk_indicators.get("voltage_violation_nodes_count", 0.0) * 0.2))

    risk_factors = {
        "n1_contingency_insecurity": round(n1_insecurity_factor, 4),
        "transmission_loading": round(loading_factor, 4),
        "critical_load_exposure": round(critical_exposure_factor, 4),
        "generation_reserve_risk": round(reserve_risk_factor, 4),
        "renewable_variability": round(renewable_variability_factor, 4),
        "battery_storage_risk": round(battery_risk_factor, 4),
        "voltage_frequency_deviation": round(voltage_dev_factor, 4),
    }

    # Weighted Composite Score (0.0 to 1.0)
    risk_index = (
        (n1_insecurity_factor * config.n1_vulnerability_weight)
        + (loading_factor * config.line_loading_weight)
        + (critical_exposure_factor * config.critical_load_exposure_weight)
        + (reserve_risk_factor * config.generation_reserve_weight)
        + (renewable_variability_factor * config.renewable_variability_weight)
        + (battery_risk_factor * config.battery_storage_weight)
        + (voltage_dev_factor * config.voltage_frequency_weight)
    )
    risk_index = float(np.clip(risk_index, 0.0, 1.0))

    risk_level = RiskThresholds.get_risk_level(risk_index)

    max_severity = max((c.risk_score for c in n1_results), default=0.0)

    return GridRiskAssessment(
        risk_index=round(risk_index, 4),
        risk_level=risk_level,
        failed_components=failed_components,
        affected_load_mw=round(base_sim.unserved_load_mw, 3),
        critical_load_at_risk=critical_at_risk,
        risk_factors=risk_factors,
        n_1_violations_count=len(n1_violations),
        most_critical_contingencies=n1_results[:5],
        ranked_critical_components=ranked_components,
        cascading_risk_score=round(max_severity, 2),
        vulnerable_assets=[rc.to_dict() for rc in ranked_components[:5]],
        summary={
            "total_contingencies_screened": len(n1_results),
            "n_1_compliant": len(n1_violations) == 0,
            "max_line_utilization_pct": base_sim.max_line_utilization_pct,
            "frequency_stability": base_sim.is_frequency_stable,
            "system_reserve_mw": round(reserve_mw, 2),
            "risk_classification": risk_level.value,
        },
    )
