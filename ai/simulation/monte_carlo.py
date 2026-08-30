"""
PULSEiQ - Monte Carlo Probabilistic Grid Simulation Engine.
Simulates thousands of stochastic grid operating states, renewable intermittency profiles,
and random equipment outage contingencies using NumPy and SciPy.
"""

from typing import Any, Dict, List, Optional, Sequence, Union
import numpy as np

from ai.models.grid import ComponentStatus, ElectricityGrid, NodeType, ScenarioConfig
from ai.simulation.models import MonteCarloDemandScenarioResult, MonteCarloSummary
from ai.simulation.power_flow import solve_power_flow


def simulate_monte_carlo_demand_scenarios(
    forecast: Any,
    num_scenarios: int = 100,
    horizon_hours: int = 24,
    uncertainty_std: float = 0.05,
    seed: int = 42,
    timestamps: Optional[List[str]] = None,
    target_id: Optional[str] = None,
    target_name: Optional[str] = None,
) -> MonteCarloDemandScenarioResult:
    """
    Executes Monte Carlo stochastic simulation over an expected XGBoost demand forecast.

    Required Flow:
        Historical demand -> XGBoost DemandForecaster -> Future demand forecast
        -> Monte Carlo simulation -> Multiple future demand scenarios -> Scenario statistics

    Args:
        forecast: ForecastResult object or list/array of hourly forecasted MW demand values.
        num_scenarios: Number of stochastic paths to generate (configurable).
        horizon_hours: Forecasting horizon length in hours (default: 24).
        uncertainty_std: Gaussian standard deviation around expected demand (default: 0.05).
        seed: Deterministic random seed for reproducibility.
        timestamps: Optional list of continuous hourly timestamps.
        target_id: Optional grid node identifier.
        target_name: Optional grid node name.

    Returns:
        MonteCarloDemandScenarioResult containing timestamps, expected forecast,
        individual scenario curves, mean, min, max, std dev, and percentiles.
    """
    if hasattr(forecast, "points"):
        # ForecastResult instance from DemandForecaster
        expected_curve = [float(pt.value_mw) for pt in forecast.points[:horizon_hours]]
        ts_list = [str(pt.timestamp) for pt in forecast.points[:horizon_hours]]
        target_id = target_id or getattr(forecast, "target_id", None)
        target_name = target_name or getattr(forecast, "target_name", None)
    elif isinstance(forecast, (list, tuple, np.ndarray)):
        expected_curve = [float(v) for v in list(forecast)[:horizon_hours]]
        ts_list = timestamps[:len(expected_curve)] if timestamps else [f"t+{i:02d}h" for i in range(len(expected_curve))]
    else:
        raise TypeError(f"Unsupported forecast input type: {type(forecast)}")

    h_len = len(expected_curve)
    if h_len == 0:
        raise ValueError("Expected forecast curve cannot be empty.")

    rng = np.random.RandomState(seed)

    # Multiplicative Gaussian stochastic variations: Y_s,t = max(0.0, mu_t * (1 + epsilon_s,t))
    noise_matrix = rng.normal(loc=0.0, scale=uncertainty_std, size=(num_scenarios, h_len))
    expected_arr = np.array(expected_curve, dtype=float)
    scenarios_arr = expected_arr * (1.0 + noise_matrix)

    # Ensure generated demand values cannot become negative
    scenarios_arr = np.maximum(0.0, scenarios_arr)

    scenario_curves = scenarios_arr.tolist()

    mean_demand = [float(np.mean(scenarios_arr[:, t])) for t in range(h_len)]
    min_demand = [float(np.min(scenarios_arr[:, t])) for t in range(h_len)]
    max_demand = [float(np.max(scenarios_arr[:, t])) for t in range(h_len)]
    std_dev = [float(np.std(scenarios_arr[:, t])) for t in range(h_len)]

    percentiles = {
        "p10": [float(np.percentile(scenarios_arr[:, t], 10)) for t in range(h_len)],
        "p25": [float(np.percentile(scenarios_arr[:, t], 25)) for t in range(h_len)],
        "p50": [float(np.percentile(scenarios_arr[:, t], 50)) for t in range(h_len)],
        "p75": [float(np.percentile(scenarios_arr[:, t], 75)) for t in range(h_len)],
        "p90": [float(np.percentile(scenarios_arr[:, t], 90)) for t in range(h_len)],
        "p95": [float(np.percentile(scenarios_arr[:, t], 95)) for t in range(h_len)],
        "p99": [float(np.percentile(scenarios_arr[:, t], 99)) for t in range(h_len)],
    }

    return MonteCarloDemandScenarioResult(
        timestamps=ts_list,
        expected_forecast=expected_curve,
        scenario_curves=scenario_curves,
        mean_scenario_demand=mean_demand,
        min_scenario_demand=min_demand,
        max_scenario_demand=max_demand,
        std_dev=std_dev,
        percentiles=percentiles,
        num_scenarios=num_scenarios,
        horizon_hours=h_len,
        uncertainty_std=uncertainty_std,
        seed=seed,
        target_id=target_id,
        target_name=target_name,
    )



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
