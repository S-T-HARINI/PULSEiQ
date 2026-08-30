"""
PULSEiQ - Grid Dispatch & Economic Optimization Engine.
Implements linear programming optimal power dispatch with generation cost curves,
battery state-of-charge tracking, transmission capacity limits, and critical load protection.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from scipy.optimize import linprog

from ai.models.grid import (
    ComponentStatus,
    ElectricityGrid,
    GridNode,
    NodeType,
    ScenarioConfig,
)
from ai.optimization.models import (
    DispatchResult,
    OptimizationConfig,
    OptimizationStatus,
)
from ai.simulation.power_flow import solve_power_flow


def solve_optimal_dispatch(
    grid: ElectricityGrid,
    config: Optional[OptimizationConfig] = None,
) -> DispatchResult:
    """
    Solves optimal economic power dispatch across all available generation, storage, and load assets.

    Optimization Objective:
        Minimize Total Cost =
            Sum(fuel_cost_i * P_gen_i)
            + Sum(cycle_cost_b * P_discharge_b)
            + Sum(curtailment_penalty * P_curt_r)
            + Sum(normal_shed_penalty * Unserved_normal_j)
            + Sum(critical_shed_penalty * Unserved_critical_k)

    Constraints:
        1. Power Balance: Total Dispatched Gen + Total Discharged Battery - Total Charged Battery
                          = Total Served Demand (Demand - Unserved)
        2. Generation Limits: P_min <= P_gen <= P_max (for online generators)
        3. Renewable Output: 0 <= P_ren_dispatched <= P_available, P_curt = P_available - P_ren_dispatched
        4. Battery Limits: -Max_Charge <= P_batt <= Max_Discharge
           SoC_{t+1} = SoC_t - (P_batt * dt / Cap) * 100 in [10%, 95%]
        5. Load Shedding Bounds: 0 <= Unserved_j <= Demand_j
    """
    if config is None:
        config = OptimizationConfig()

    active_gens = [
        n for n in grid.nodes.values()
        if n.is_operational and n.node_type == NodeType.GENERATOR
    ]
    active_solar = [
        n for n in grid.nodes.values()
        if n.is_operational and n.node_type == NodeType.SOLAR
    ]
    active_wind = [
        n for n in grid.nodes.values()
        if n.is_operational and n.node_type == NodeType.WIND
    ]
    active_batteries = [
        n for n in grid.nodes.values()
        if n.is_operational and n.node_type == NodeType.BATTERY
    ]
    active_loads = [
        n for n in grid.nodes.values()
        if n.is_operational and n.node_type in (NodeType.LOAD_NORMAL, NodeType.LOAD_CRITICAL)
    ]

    total_demand = sum(n.operational.demand_mw for n in active_loads)
    total_critical_demand = sum(
        n.operational.demand_mw for n in active_loads if n.is_critical
    )

    # Variables mapping
    # x = [
    #   P_gen (len active_gens),
    #   P_solar_disp (len active_solar),
    #   P_solar_curt (len active_solar),
    #   P_wind_disp (len active_wind),
    #   P_wind_curt (len active_wind),
    #   P_batt_discharge (len active_batteries),
    #   P_batt_charge (len active_batteries),
    #   Unserved_load (len active_loads)
    # ]

    c_obj = []
    bounds = []

    # 1. Generators
    for g in active_gens:
        cost = config.fuel_cost_per_mwh.get("gas_ccgt", 45.0)
        c_obj.append(cost)
        p_min = max(0.0, g.operational.min_capacity_mw)
        p_max = max(p_min, g.operational.max_capacity_mw)
        bounds.append((p_min, p_max))

    # 2. Solar (Dispatched + Curtailed)
    for s in active_solar:
        p_avail = s.operational.max_capacity_mw or s.operational.generation_mw
        c_obj.append(0.0)  # zero fuel cost
        bounds.append((0.0, p_avail))
        c_obj.append(config.renewable_curtailment_penalty)
        bounds.append((0.0, p_avail))

    # 3. Wind (Dispatched + Curtailed)
    for w in active_wind:
        p_avail = w.operational.max_capacity_mw or w.operational.generation_mw
        c_obj.append(0.0)
        bounds.append((0.0, p_avail))
        c_obj.append(config.renewable_curtailment_penalty)
        bounds.append((0.0, p_avail))

    # 4. Batteries (Discharge + Charge)
    for b in active_batteries:
        p_max = b.operational.battery_max_power_mw or b.operational.max_capacity_mw or 15.0
        soc_pct = b.operational.battery_soc_pct
        cap_mwh = b.operational.battery_capacity_mwh or 40.0

        # Available discharge energy above 10% SoC
        max_discharge_mw = min(p_max, max(0.0, ((soc_pct - 10.0) / 100.0) * cap_mwh / config.time_step_hours))
        # Available charge energy below 95% SoC
        max_charge_mw = min(p_max, max(0.0, ((95.0 - soc_pct) / 100.0) * cap_mwh / config.time_step_hours))

        c_obj.append(config.battery_cycle_cost)
        bounds.append((0.0, max_discharge_mw))
        c_obj.append(config.fuel_cost_per_mwh.get("battery", 5.0))
        bounds.append((0.0, max_charge_mw))

    # 5. Unserved Load
    for ld in active_loads:
        d_val = ld.operational.demand_mw
        if ld.is_critical:
            penalty = config.critical_load_shedding_penalty
        else:
            penalty = config.normal_load_shedding_penalty
        c_obj.append(penalty)
        bounds.append((0.0, d_val))

    # Equality Constraints (A_eq * x = b_eq)
    # A) Power Balance:
    # Sum(P_gen) + Sum(P_solar_disp) + Sum(P_wind_disp) + Sum(P_batt_discharge) - Sum(P_batt_charge)
    #   + Sum(Unserved_load) = Total Demand
    A_eq = []
    b_eq = []

    bal_row = []
    # Gen
    for _ in active_gens:
        bal_row.append(1.0)
    # Solar (disp + curt)
    for _ in active_solar:
        bal_row.extend([1.0, 0.0])
    # Wind (disp + curt)
    for _ in active_wind:
        bal_row.extend([1.0, 0.0])
    # Battery (discharge - charge)
    for _ in active_batteries:
        bal_row.extend([1.0, -1.0])
    # Unserved load
    for _ in active_loads:
        bal_row.append(1.0)

    A_eq.append(bal_row)
    b_eq.append(total_demand)

    # B) Solar Availability: P_solar_disp + P_solar_curt = P_avail
    curr_idx = len(active_gens)
    for s in active_solar:
        p_avail = s.operational.max_capacity_mw or s.operational.generation_mw
        row = [0.0] * len(c_obj)
        row[curr_idx] = 1.0      # disp
        row[curr_idx + 1] = 1.0  # curt
        A_eq.append(row)
        b_eq.append(p_avail)
        curr_idx += 2

    # C) Wind Availability: P_wind_disp + P_wind_curt = P_avail
    for w in active_wind:
        p_avail = w.operational.max_capacity_mw or w.operational.generation_mw
        row = [0.0] * len(c_obj)
        row[curr_idx] = 1.0      # disp
        row[curr_idx + 1] = 1.0  # curt
        A_eq.append(row)
        b_eq.append(p_avail)
        curr_idx += 2

    # Solve LP via SciPy HiGHS simplex/interior-point solver
    res = linprog(
        c=c_obj,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )

    if not res.success:
        return DispatchResult(
            status=OptimizationStatus.INFEASIBLE,
            total_cost=0.0,
            summary={"message": res.message},
        )

    x_opt = res.x
    var_idx = 0

    gen_dispatch: Dict[str, float] = {}
    for g in active_gens:
        gen_dispatch[g.id] = float(x_opt[var_idx])
        var_idx += 1

    curtailed_renewables: Dict[str, float] = {}
    for s in active_solar:
        gen_dispatch[s.id] = float(x_opt[var_idx])
        curtailed_renewables[s.id] = float(x_opt[var_idx + 1])
        var_idx += 2

    for w in active_wind:
        gen_dispatch[w.id] = float(x_opt[var_idx])
        curtailed_renewables[w.id] = float(x_opt[var_idx + 1])
        var_idx += 2

    batt_dispatch: Dict[str, float] = {}
    batt_soc_after: Dict[str, float] = {}
    for b in active_batteries:
        p_dis = float(x_opt[var_idx])
        p_chg = float(x_opt[var_idx + 1])
        net_batt = p_dis - p_chg  # positive is discharge
        batt_dispatch[b.id] = net_batt

        cap_mwh = b.operational.battery_capacity_mwh or 40.0
        delta_soc = (net_batt * config.time_step_hours / cap_mwh) * 100.0
        new_soc = float(np.clip(b.operational.battery_soc_pct - delta_soc, 0.0, 100.0))
        batt_soc_after[b.id] = new_soc
        var_idx += 2

    unserved_demand: Dict[str, float] = {}
    critical_unserved = 0.0
    for ld in active_loads:
        u_val = float(x_opt[var_idx])
        unserved_demand[ld.id] = u_val
        if ld.is_critical:
            critical_unserved += u_val
        var_idx += 1

    total_dispatched_gen = sum(gen_dispatch.values())
    total_served_demand = total_demand - sum(unserved_demand.values())
    critical_served_pct = 100.0
    if total_critical_demand > 0:
        critical_served_pct = ((total_critical_demand - critical_unserved) / total_critical_demand) * 100.0

    # Post-dispatch line flow validation
    temp_grid = grid.apply_scenario(ScenarioConfig())
    for nid, p_mw in gen_dispatch.items():
        if nid in temp_grid.nodes:
            temp_grid.nodes[nid].operational.generation_mw = p_mw
    for nid, u_mw in unserved_demand.items():
        if nid in temp_grid.nodes:
            temp_grid.nodes[nid].operational.demand_mw -= u_mw

    pf_res = solve_power_flow(temp_grid)

    line_flows = {lid: lr.flow_mw for lid, lr in pf_res.line_results.items()}
    line_utils = {lid: lr.utilization_pct for lid, lr in pf_res.line_results.items()}

    return DispatchResult(
        status=OptimizationStatus.OPTIMAL,
        total_cost=float(res.fun),
        total_generation_dispatched_mw=round(total_dispatched_gen, 3),
        total_demand_served_mw=round(total_served_demand, 3),
        critical_unserved_mw=round(critical_unserved, 3),
        critical_load_served_pct=round(critical_served_pct, 2),
        generator_dispatch_mw=gen_dispatch,
        battery_dispatch_mw=batt_dispatch,
        battery_soc_after_pct=batt_soc_after,
        curtailed_renewable_mw=curtailed_renewables,
        unserved_demand_mw=unserved_demand,
        line_flows_mw=line_flows,
        line_utilizations_pct=line_utils,
        summary={
            "solver": "HiGHS-LP",
            "iterations": res.nit,
            "total_demand_mw": total_demand,
            "total_curtailed_mw": sum(curtailed_renewables.values()),
            "total_unserved_mw": sum(unserved_demand.values()),
            "max_line_utilization_pct": pf_res.max_line_utilization_pct,
        },
    )
