"""
PULSEiQ - Monte Carlo Probabilistic Grid Simulation Engine.
Simulates thousands of stochastic grid operating states, renewable intermittency profiles,
and random equipment outage contingencies using NumPy and SciPy.
"""

from typing import Dict, List, Optional
import numpy as np

from ai.models.grid import ComponentStatus, ElectricityGrid, NodeType, ScenarioConfig
from ai.simulation.models import MonteCarloSummary
from ai.simulation.power_flow import solve_power_flow


def run_monte_carlo_simulation(
    grid: ElectricityGrid,
    iterations: int = 500,
    load_uncertainty_std: float = 0.05,
    renewable_uncertainty_std: float = 0.15,
    seed: int = 42,
) -> MonteCarloSummary:
    """
    Executes Monte Carlo probabilistic grid simulation.

    Args:
        grid: Base ElectricityGrid.
        iterations: Number of stochastic trials (default: 500).
        load_uncertainty_std: Gaussian std dev for demand variations.
        renewable_uncertainty_std: Gaussian std dev for renewable intermittency.
        seed: PRNG seed for deterministic reproducibility.

    Returns:
        MonteCarloSummary containing LOLP, EUE, line overload frequencies, and risk metrics.
    """
    rng = np.random.RandomState(seed)

    loss_of_load_count = 0
    unserved_mw_list: List[float] = []
    line_overload_counts: Dict[str, int] = {lid: 0 for lid in grid.lines.keys()}
    asset_trip_counts: Dict[str, int] = {
        **{nid: 0 for nid in grid.nodes.keys()},
        **{lid: 0 for lid in grid.lines.keys()},
    }
    overload_event_count = 0

    base_nodes = list(grid.nodes.values())
    base_lines = list(grid.lines.values())

    for it in range(iterations):
        # 1. Sample Stochastic Component Outages via Bernoulli trials
        tripped_ids: List[str] = []

        for node in base_nodes:
            p_fail = max(0.0001, node.risk.failure_probability)
            if rng.uniform(0.0, 1.0) < p_fail:
                tripped_ids.append(node.id)
                asset_trip_counts[node.id] += 1

        for line in base_lines:
            p_fail = max(0.0001, line.risk.failure_probability)
            if rng.uniform(0.0, 1.0) < p_fail:
                tripped_ids.append(line.id)
                asset_trip_counts[line.id] += 1

        # 2. Sample Stochastic Load Multiplier & Renewable Multipliers
        demand_mult = max(0.6, float(1.0 + rng.normal(0.0, load_uncertainty_std)))
        solar_mult = max(0.0, float(1.0 + rng.normal(0.0, renewable_uncertainty_std)))
        wind_mult = max(0.0, float(1.0 + rng.normal(0.0, renewable_uncertainty_std)))

        scenario = ScenarioConfig(
            name=f"MonteCarlo_Iter_{it}",
            demand_multiplier=demand_mult,
            solar_multiplier=solar_mult,
            wind_multiplier=wind_mult,
            battery_availability=True,
            contingencies=tripped_ids,
        )

        # 3. Apply Scenario to Grid Copy & Solve Power Flow
        iter_grid = grid.apply_scenario(scenario)
        sim_res = solve_power_flow(iter_grid)

        # 4. Record Metrics
        unserved = sim_res.unserved_load_mw
        unserved_mw_list.append(unserved)

        if unserved > 0.1:
            loss_of_load_count += 1

        has_overload = False
        for lid, line_res in sim_res.line_results.items():
            if line_res.is_overloaded:
                line_overload_counts[lid] += 1
                has_overload = True

        if has_overload:
            overload_event_count += 1

    # 5. Compute Statistical Aggregates
    lolp = loss_of_load_count / max(iterations, 1)
    eue_mwh = sum(unserved_mw_list) / max(iterations, 1)  # Assuming 1-hour time slices
    overload_prob = overload_event_count / max(iterations, 1)
    worst_case_unserved = max(unserved_mw_list) if unserved_mw_list else 0.0
    avg_unserved = sum(unserved_mw_list) / max(len(unserved_mw_list), 1)

    line_overload_probs = {
        lid: count / max(iterations, 1) for lid, count in line_overload_counts.items()
    }

    # Normalized composite risk score (0 to 100)
    composite_risk = min(
        100.0,
        (lolp * 50.0) + (overload_prob * 30.0) + min(20.0, (eue_mwh / 10.0) * 20.0),
    )

    return MonteCarloSummary(
        iterations_count=iterations,
        loss_of_load_probability=lolp,
        expected_unserved_energy_mwh=eue_mwh,
        loss_of_load_events=loss_of_load_count,
        overload_probability=overload_prob,
        worst_case_unserved_mw=worst_case_unserved,
        average_unserved_mw=avg_unserved,
        line_overload_probabilities=line_overload_probs,
        asset_trip_frequencies=asset_trip_counts,
        risk_score=composite_risk,
    )
