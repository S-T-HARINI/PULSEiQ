"""
PULSEiQ - Grid Risk & Contingency Assessment Engine.
Implements N-1 screening, N-k multi-contingency analysis, cascading thermal overload simulation,
and standardized grid risk scoring for backend/API consumption.
"""

from itertools import combinations
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from ai.graph.builder import find_articulation_points, find_bridges, grid_to_networkx
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
    ContingencyResult,
    ContingencyType,
    GridRiskAssessment,
    RiskLevel,
)
from ai.simulation.power_flow import solve_power_flow


def evaluate_contingency(
    grid: ElectricityGrid,
    contingency_id: str,
    tripped_ids: List[str],
    contingency_type: ContingencyType,
) -> ContingencyResult:
    """
    Evaluates power flow, line overloads, and unserved critical loads under a specific outage contingency.
    """
    # Create scenario and apply to grid copy
    scenario = ScenarioConfig(
        name=f"Contingency_{contingency_id}",
        contingencies=tripped_ids,
    )
    tripped_grid = grid.apply_scenario(scenario)

    # Solve power flow on post-contingency grid
    sim_res = solve_power_flow(tripped_grid)

    overloaded_lines = [
        lid for lid, lres in sim_res.line_results.items()
        if lres.is_overloaded and lid not in tripped_ids
    ]

    # Graph connectivity check to find isolated/islanded load nodes
    G = grid_to_networkx(tripped_grid, active_only=True)
    isolated_nodes = []
    critical_load_lost_mw = 0.0
    critical_at_risk = False

    # Check unserved demand on critical loads
    for node in grid.nodes.values():
        if node.is_critical and node.operational.demand_mw > 0:
            if node.id in tripped_ids or node.id not in G:
                isolated_nodes.append(node.id)
                critical_load_lost_mw += node.operational.demand_mw
                critical_at_risk = True
            elif sim_res.unserved_load_mw > 0.1 and sim_res.power_imbalance_mw < -0.1:
                # Under-generation affects grid-wide critical reliability
                critical_at_risk = True

    is_secure = (
        len(overloaded_lines) == 0
        and sim_res.unserved_load_mw <= 0.1
        and sim_res.is_frequency_stable
        and not critical_at_risk
    )

    # Compute severity score (0 to 100)
    unserved_mw = sim_res.unserved_load_mw + critical_load_lost_mw
    overload_penalty = len(overloaded_lines) * 15.0 + max(0.0, sim_res.max_line_utilization_pct - 100.0) * 0.5
    loss_of_load_penalty = (unserved_mw / max(grid.total_demand_mw, 1.0)) * 50.0
    critical_penalty = 30.0 if critical_at_risk else 0.0
    freq_penalty = 15.0 if not sim_res.is_frequency_stable else 0.0

    severity = min(100.0, overload_penalty + loss_of_load_penalty + critical_penalty + freq_penalty)

    return ContingencyResult(
        contingency_id=contingency_id,
        tripped_components=tripped_ids,
        contingency_type=contingency_type,
        is_secure=is_secure,
        unserved_load_mw=round(unserved_mw, 3),
        critical_load_affected_mw=round(critical_load_lost_mw, 3),
        critical_load_at_risk=critical_at_risk,
        overloaded_lines=overloaded_lines,
        max_line_utilization_pct=round(sim_res.max_line_utilization_pct, 2),
        isolated_nodes=isolated_nodes,
        frequency_hz=round(sim_res.frequency_hz, 4),
        severity_score=round(severity, 2),
    )


def run_n_1_analysis(
    grid: ElectricityGrid,
    top_n_worst: int = 10,
) -> List[ContingencyResult]:
    """
    Exhaustively evaluates all N-1 line and generator outages.
    Returns results sorted by severity descending.
    """
    results: List[ContingencyResult] = []

    # 1. Test all transmission lines
    for line_id, line in grid.lines.items():
        if not line.is_operational:
            continue
        c_res = evaluate_contingency(
            grid=grid,
            contingency_id=f"N-1_{line_id}",
            tripped_ids=[line_id],
            contingency_type=ContingencyType.N_MINUS_1_LINE,
        )
        results.append(c_res)

    # 2. Test all generation assets
    for node_id, node in grid.nodes.items():
        if not node.is_operational or node.node_type not in (NodeType.GENERATOR, NodeType.SOLAR, NodeType.WIND):
            continue
        c_res = evaluate_contingency(
            grid=grid,
            contingency_id=f"N-1_{node_id}",
            tripped_ids=[node_id],
            contingency_type=ContingencyType.N_MINUS_1_GEN,
        )
        results.append(c_res)

    results.sort(key=lambda x: x.severity_score, reverse=True)
    return results[:top_n_worst] if top_n_worst > 0 else results


def run_n_k_analysis(
    grid: ElectricityGrid,
    k: int = 2,
    max_combinations: int = 30,
) -> List[ContingencyResult]:
    """
    Evaluates high-impact multi-component N-k outages (k=2 by default).
    Prioritizes combinations of high-criticality and high-capacity assets.
    """
    candidate_assets: List[Tuple[str, float]] = []

    # Prioritize critical lines and large generators
    for lid, line in grid.lines.items():
        weight = line.capacity_mw * (2.0 if line.risk.criticality == CriticalityLevel.CRITICAL else 1.0)
        candidate_assets.append((lid, weight))

    for nid, node in grid.nodes.items():
        if node.node_type in (NodeType.GENERATOR, NodeType.SOLAR, NodeType.WIND, NodeType.BATTERY):
            weight = node.operational.max_capacity_mw * 1.5
            candidate_assets.append((nid, weight))

    # Sort candidates by impact weight and take top candidates
    candidate_assets.sort(key=lambda x: x[1], reverse=True)
    top_candidates = [c[0] for c in candidate_assets[:12]]

    combos = list(combinations(top_candidates, k))[:max_combinations]
    results: List[ContingencyResult] = []

    for i, combo in enumerate(combos):
        c_id = f"N-{k}_{'_'.join(combo)}"
        c_res = evaluate_contingency(
            grid=grid,
            contingency_id=c_id,
            tripped_ids=list(combo),
            contingency_type=ContingencyType.N_MINUS_K,
        )
        results.append(c_res)

    results.sort(key=lambda x: x.severity_score, reverse=True)
    return results


def simulate_cascading_failure(
    grid: ElectricityGrid,
    initial_trips: List[str],
    overload_threshold_pct: float = 115.0,
    max_stages: int = 8,
) -> CascadingFailureReport:
    """
    Simulates sequential cascading line outages triggered by thermal overloads.
    """
    current_trips = list(initial_trips)
    stages: List[CascadingStage] = []
    current_grid = grid

    for stage_idx in range(max_stages):
        scenario = ScenarioConfig(
            name=f"Cascade_Stage_{stage_idx}",
            contingencies=current_trips,
        )
        post_grid = current_grid.apply_scenario(scenario)
        sim_res = solve_power_flow(post_grid)

        # Find newly overloaded operational lines exceeding trip threshold
        new_overloaded = [
            lid for lid, lres in sim_res.line_results.items()
            if lres.utilization_pct >= overload_threshold_pct and lid not in current_trips
        ]

        stage_record = CascadingStage(
            stage_index=stage_idx + 1,
            newly_tripped_lines=new_overloaded,
            overloaded_lines_before_trip=[
                lid for lid, lres in sim_res.line_results.items() if lres.is_overloaded
            ],
            unserved_load_mw=sim_res.unserved_load_mw,
            system_frequency_hz=sim_res.frequency_hz,
        )
        stages.append(stage_record)

        if not new_overloaded:
            # Grid stabilized, cascade halts
            break

        # Trip all overloaded lines in the next stage
        current_trips.extend(new_overloaded)

    final_sim = solve_power_flow(grid.apply_scenario(ScenarioConfig(contingencies=current_trips)))
    final_unserved = final_sim.unserved_load_mw
    total_lines_lost = len(current_trips)
    blackout = final_unserved >= 0.80 * grid.total_demand_mw

    cascade_score = min(
        100.0,
        (len(stages) * 12.0)
        + (total_lines_lost * 8.0)
        + (final_unserved / max(grid.total_demand_mw, 1.0)) * 50.0,
    )

    return CascadingFailureReport(
        initiating_contingency=initial_trips,
        total_stages=len(stages),
        stages=stages,
        final_unserved_mw=round(final_unserved, 3),
        final_critical_unserved_mw=round(
            sum(
                n.operational.demand_mw for n in grid.nodes.values()
                if n.is_critical and (n.id in current_trips or final_unserved > 10.0)
            ),
            3,
        ),
        blackout_occurred=blackout,
        total_lines_lost=total_lines_lost,
        cascade_risk_score=round(cascade_score, 2),
    )


def calculate_grid_risk_index(
    grid: ElectricityGrid,
) -> GridRiskAssessment:
    """
    Computes standard overall grid risk scorecard for PULSEiQ.
    Outputs structured summary matching FastAPI contract specifications.
    """
    n1_results = run_n_1_analysis(grid, top_n_worst=15)
    n1_violations = [c for c in n1_results if not c.is_secure]

    # Baseline operating state simulation
    base_sim = solve_power_flow(grid)

    failed_components = [
        nid for nid, n in grid.nodes.items() if not n.is_operational
    ] + [
        lid for lid, l in grid.lines.items() if not l.is_operational
    ]

    # Graph structural vulnerability
    G = grid_to_networkx(grid)
    articulation_pts = find_articulation_points(G)
    bridges = find_bridges(G)

    # Compute continuous risk index (0.0 to 1.0)
    n1_insecurity_ratio = len(n1_violations) / max(len(n1_results), 1)
    max_severity = max((c.severity_score for c in n1_results), default=0.0) / 100.0
    loading_factor = min(1.0, base_sim.max_line_utilization_pct / 100.0)
    unserved_factor = min(1.0, base_sim.unserved_load_mw / max(grid.total_demand_mw, 1.0))

    risk_index = (
        (n1_insecurity_ratio * 0.35)
        + (max_severity * 0.35)
        + (loading_factor * 0.20)
        + (unserved_factor * 0.10)
    )
    risk_index = float(np.clip(risk_index, 0.0, 1.0))

    # Categorical Risk Level
    if risk_index < 0.20:
        risk_level = RiskLevel.LOW
    elif risk_index < 0.45:
        risk_level = RiskLevel.MODERATE
    elif risk_index < 0.70:
        risk_level = RiskLevel.HIGH
    elif risk_index < 0.88:
        risk_level = RiskLevel.CRITICAL
    else:
        risk_level = RiskLevel.EXTREME

    # Check if any critical load is currently impacted or vulnerable to N-1
    critical_at_risk = any(c.critical_load_at_risk for c in n1_violations) or base_sim.unserved_load_mw > 0.1

    vulnerable_assets = []
    for pt in articulation_pts:
        node = grid.get_node(pt)
        if node:
            vulnerable_assets.append({
                "id": node.id,
                "name": node.name,
                "type": "articulation_node",
                "criticality": node.risk.criticality.value,
                "description": "Cut vertex: failure splits grid into isolated islands",
            })

    for br in bridges:
        vulnerable_assets.append({
            "id": f"{br[0]}--{br[1]}",
            "name": f"Line {br[0]} to {br[1]}",
            "type": "bridge_line",
            "criticality": "high",
            "description": "Bridge line: loss results in immediate radial load disconnection",
        })

    return GridRiskAssessment(
        risk_index=round(risk_index, 4),
        risk_level=risk_level,
        failed_components=failed_components,
        affected_load_mw=round(base_sim.unserved_load_mw, 3),
        critical_load_at_risk=critical_at_risk,
        n_1_violations_count=len(n1_violations),
        most_critical_contingencies=n1_results[:5],
        cascading_risk_score=round(max_severity * 100.0, 2),
        vulnerable_assets=vulnerable_assets,
        summary={
            "total_contingencies_screened": len(n1_results),
            "n_1_compliant": len(n1_violations) == 0,
            "max_line_utilization_pct": base_sim.max_line_utilization_pct,
            "frequency_stability": base_sim.is_frequency_stable,
            "system_reserve_mw": round(grid.total_generation_mw - grid.total_demand_mw, 2),
        },
    )
