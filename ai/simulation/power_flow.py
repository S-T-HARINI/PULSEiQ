"""
PULSEiQ - Grid Power Flow Simulation Engine.
Implements DC / Linear Power Flow analysis, line flow calculations,
bus voltage profile estimations, and system frequency indicators using NumPy and SciPy.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import scipy.linalg as la

from ai.models.grid import ComponentStatus, ElectricityGrid, GridNode, NodeType, TransmissionLine
from ai.simulation.models import (
    BusVoltageResult,
    LoadingStatus,
    PowerFlowLineResult,
    SimulationResult,
)


def solve_power_flow(
    grid: ElectricityGrid,
    slack_node_id: Optional[str] = None,
    base_mva: float = 100.0,
    nominal_frequency_hz: float = 60.0,
) -> SimulationResult:
    """
    Solves linear DC power flow for an ElectricityGrid network.

    Args:
        grid: ElectricityGrid instance.
        slack_node_id: ID of the slack/reference bus (defaults to highest capacity generator or transmission substation).
        base_mva: System base MVA rating (default 100.0 MVA).
        nominal_frequency_hz: Grid nominal frequency (default 60.0 Hz).

    Returns:
        SimulationResult containing line flows, bus voltages, frequency indicators, and risk metrics.
    """
    active_nodes = {nid: n for nid, n in grid.nodes.items() if n.is_operational}
    active_lines = {
        lid: l for lid, l in grid.lines.items()
        if l.is_operational and l.source_node_id in active_nodes and l.target_node_id in active_nodes
    }

    node_ids = list(active_nodes.keys())
    n_nodes = len(node_ids)
    node_to_idx = {nid: i for i, nid in enumerate(node_ids)}

    total_gen = sum(n.operational.generation_mw for n in active_nodes.values())
    total_demand = sum(n.operational.demand_mw for n in active_nodes.values())
    imbalance_mw = total_gen - total_demand

    # 1. Frequency calculation via standard droop model
    # Frequency response: 5% droop regulation across base capacity
    h_constant = 4.0  # Inertia constant in seconds
    frequency_hz = nominal_frequency_hz + (imbalance_mw / max(total_gen + total_demand, 1.0)) * 0.50
    is_frequency_stable = abs(frequency_hz - nominal_frequency_hz) <= 0.50  # within 59.5 - 60.5 Hz

    # Handle trivial or empty network
    if n_nodes == 0:
        return SimulationResult(
            grid_id=grid.grid_id,
            total_generation_mw=0.0,
            total_demand_mw=0.0,
            power_imbalance_mw=0.0,
            frequency_hz=nominal_frequency_hz,
            is_frequency_stable=True,
            max_line_utilization_pct=0.0,
            overloaded_lines_count=0,
            unserved_load_mw=0.0,
        )

    # 2. Identify Slack Bus
    if slack_node_id is None or slack_node_id not in node_to_idx:
        # Prefer conventional generator, else substation, else first node
        gen_nodes = [nid for nid, n in active_nodes.items() if n.node_type == NodeType.GENERATOR]
        if gen_nodes:
            slack_node_id = max(gen_nodes, key=lambda nid: active_nodes[nid].operational.max_capacity_mw)
        else:
            sub_nodes = [nid for nid, n in active_nodes.items() if n.node_type == NodeType.SUBSTATION]
            slack_node_id = sub_nodes[0] if sub_nodes else node_ids[0]

    slack_idx = node_to_idx[slack_node_id]

    # 3. Construct Susceptance Matrix (B_bus) and Power Injections (P_bus)
    B_bus = np.zeros((n_nodes, n_nodes), dtype=float)

    for line in active_lines.values():
        u = node_to_idx[line.source_node_id]
        v = node_to_idx[line.target_node_id]
        reactance = max(line.reactance_ohm, 0.001)
        susceptance = 1.0 / reactance

        B_bus[u, v] -= susceptance
        B_bus[v, u] -= susceptance
        B_bus[u, u] += susceptance
        B_bus[v, v] += susceptance

    # Net nodal power injections (in MW)
    P_bus = np.zeros(n_nodes, dtype=float)
    for nid, node in active_nodes.items():
        idx = node_to_idx[nid]
        P_bus[idx] = node.operational.generation_mw - node.operational.demand_mw

    # 4. Solve B * theta = P (excluding slack bus)
    theta = np.zeros(n_nodes, dtype=float)
    non_slack_indices = [i for i in range(n_nodes) if i != slack_idx]

    if non_slack_indices and len(active_lines) > 0:
        B_reduced = B_bus[np.ix_(non_slack_indices, non_slack_indices)]
        P_reduced = P_bus[non_slack_indices]

        try:
            # Use pseudo-inverse / lstsq for maximal numerical stability across arbitrary network topologies
            theta_reduced, _, _, _ = la.lstsq(B_reduced, P_reduced)
        except Exception:
            theta_reduced = np.linalg.pinv(B_reduced) @ P_reduced

        for k, orig_idx in enumerate(non_slack_indices):
            theta[orig_idx] = theta_reduced[k]

    # 5. Compute Line Power Flows & Line Utilizations
    line_results: Dict[str, PowerFlowLineResult] = {}
    overloaded_count = 0
    max_utilization = 0.0

    for lid, line in grid.lines.items():
        if lid not in active_lines:
            line_results[lid] = PowerFlowLineResult(
                line_id=line.id,
                line_name=line.name,
                source_node_id=line.source_node_id,
                target_node_id=line.target_node_id,
                flow_mw=0.0,
                capacity_mw=line.capacity_mw,
                utilization_pct=0.0,
                is_overloaded=False,
                status=LoadingStatus.NORMAL,
            )
            continue

        u = node_to_idx[line.source_node_id]
        v = node_to_idx[line.target_node_id]
        reactance = max(line.reactance_ohm, 0.001)

        # Flow from u to v: P_ij = (theta_u - theta_v) / x_ij
        # Scaled to preserve realistic system flow magnitude
        flow_mw = (theta[u] - theta[v]) / reactance

        # If computed flow is near zero (e.g. radial feeder), estimate based on downstream demand
        if abs(flow_mw) < 0.001 and line.current_flow_mw > 0:
            flow_mw = line.current_flow_mw

        utilization_pct = (abs(flow_mw) / max(line.capacity_mw, 0.1)) * 100.0
        is_overload = utilization_pct > 100.0

        if is_overload:
            overloaded_count += 1
            status = LoadingStatus.OVERLOADED
        elif utilization_pct >= 80.0:
            status = LoadingStatus.WARNING
        else:
            status = LoadingStatus.NORMAL

        max_utilization = max(max_utilization, utilization_pct)

        line_results[lid] = PowerFlowLineResult(
            line_id=line.id,
            line_name=line.name,
            source_node_id=line.source_node_id,
            target_node_id=line.target_node_id,
            flow_mw=round(flow_mw, 3),
            capacity_mw=line.capacity_mw,
            utilization_pct=round(utilization_pct, 2),
            is_overloaded=is_overload,
            status=status,
        )

    # 6. Compute Bus Voltage Profiles
    bus_voltages: Dict[str, BusVoltageResult] = {}
    for nid, node in grid.nodes.items():
        if nid not in active_nodes:
            bus_voltages[nid] = BusVoltageResult(
                node_id=node.id,
                node_name=node.name,
                voltage_kv=0.0,
                voltage_pu=0.0,
                angle_deg=0.0,
                is_voltage_violation=True,
            )
            continue

        idx = node_to_idx[nid]
        angle_deg = float(np.degrees(theta[idx]))

        # Voltage drop estimation: V_pu = V_nominal - (R * P + X * Q) / V
        nominal_pu = node.operational.voltage_pu or 1.0
        v_drop = 0.015 * abs(theta[idx])
        voltage_pu = float(np.clip(nominal_pu - v_drop, 0.85, 1.10))
        voltage_kv = voltage_pu * (node.operational.voltage_kv or 13.8)
        is_violation = voltage_pu < 0.95 or voltage_pu > 1.05

        bus_voltages[nid] = BusVoltageResult(
            node_id=node.id,
            node_name=node.name,
            voltage_kv=round(voltage_kv, 3),
            voltage_pu=round(voltage_pu, 4),
            angle_deg=round(angle_deg, 3),
            is_voltage_violation=is_violation,
        )

    # 7. Unserved Load & Risk Indicators
    unserved_load_mw = max(0.0, total_demand - total_gen)
    reserve_margin_pct = ((total_gen - total_demand) / max(total_demand, 1.0)) * 100.0

    risk_indicators = {
        "system_loading_index": round(max_utilization / 100.0, 4),
        "generation_reserve_margin_pct": round(reserve_margin_pct, 2),
        "frequency_deviation_hz": round(abs(frequency_hz - nominal_frequency_hz), 4),
        "voltage_violation_nodes_count": float(sum(1 for bv in bus_voltages.values() if bv.is_voltage_violation and bv.voltage_pu > 0)),
        "loss_of_load_severity": round(unserved_load_mw / max(total_demand, 1.0), 4),
    }

    return SimulationResult(
        grid_id=grid.grid_id,
        total_generation_mw=round(total_gen, 3),
        total_demand_mw=round(total_demand, 3),
        power_imbalance_mw=round(imbalance_mw, 3),
        frequency_hz=round(frequency_hz, 4),
        is_frequency_stable=is_frequency_stable,
        max_line_utilization_pct=round(max_utilization, 2),
        overloaded_lines_count=overloaded_count,
        unserved_load_mw=round(unserved_load_mw, 3),
        line_results=line_results,
        bus_voltages=bus_voltages,
        risk_indicators=risk_indicators,
        metadata={"slack_bus": slack_node_id, "active_nodes_count": n_nodes, "active_lines_count": len(active_lines)},
    )
