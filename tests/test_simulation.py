"""
Unit tests for PULSEiQ Power Flow & Monte Carlo Simulation Module.
"""

import pytest
from ai.models.grid import ScenarioConfig
from ai.models.mock_grid import create_mock_grid
from ai.simulation import (
    LoadingStatus,
    run_monte_carlo_simulation,
    solve_power_flow,
)


def test_solve_power_flow_baseline():
    """Verify linear power flow solution on the baseline demonstration grid."""
    grid = create_mock_grid()
    res = solve_power_flow(grid)

    assert res.grid_id == grid.grid_id
    assert res.total_generation_mw > 100.0
    assert res.total_demand_mw > 100.0
    assert 59.0 <= res.frequency_hz <= 61.0
    assert res.is_frequency_stable is True
    assert len(res.line_results) == len(grid.lines)
    assert len(res.bus_voltages) == len(grid.nodes)

    # In baseline state with all lines operational, no severe overload
    assert res.overloaded_lines_count == 0
    assert res.max_line_utilization_pct < 100.0

    # Line results check
    gen_line = res.line_results["line_gen_to_submain"]
    assert gen_line.flow_mw > 50.0
    assert gen_line.status == LoadingStatus.NORMAL


def test_solve_power_flow_heavy_load_scenario():
    """Verify power flow identifies line overloads under stressed conditions."""
    grid = create_mock_grid()

    # Apply severe load surge (+80% demand)
    stressed_grid = grid.apply_scenario(ScenarioConfig(demand_multiplier=1.8))
    res = solve_power_flow(stressed_grid)

    assert res.total_demand_mw > grid.total_demand_mw
    assert res.max_line_utilization_pct > 80.0
    assert "loss_of_load_severity" in res.risk_indicators


def test_monte_carlo_simulation():
    """Verify probabilistic Monte Carlo grid simulation."""
    grid = create_mock_grid()
    mc_res = run_monte_carlo_simulation(grid, iterations=40, seed=42)

    assert mc_res.iterations_count == 40
    assert 0.0 <= mc_res.loss_of_load_probability <= 1.0
    assert mc_res.expected_unserved_energy_mwh >= 0.0
    assert 0.0 <= mc_res.overload_probability <= 1.0
    assert 0.0 <= mc_res.risk_score <= 100.0
    assert len(mc_res.line_overload_probabilities) == len(grid.lines)

    # Test serialization
    data = mc_res.to_dict()
    assert "loss_of_load_probability" in data
    assert "expected_unserved_energy_mwh" in data
    assert "risk_score" in data


def test_monte_carlo_demand_forecast_integration_24h():
    """
    Verify integration between real XGBoost DemandForecaster and Monte Carlo simulation:
    - Forecast passes directly into Monte Carlo
    - Exact 24 hourly timestamps
    - Correct number of scenarios (50)
    - Numeric, non-negative values
    - Correct mean and percentile bounds
    """
    import numpy as np
    from ai.forecasting import DemandForecaster
    from ai.simulation import (
        MonteCarloDemandScenarioResult,
        simulate_monte_carlo_demand_scenarios,
    )

    grid = create_mock_grid()
    hospital_node = grid.get_node("load_hospital_main")

    forecaster = DemandForecaster(seed=42)
    forecast_res = forecaster.predict(hospital_node, horizon_hours=24)

    mc_res = simulate_monte_carlo_demand_scenarios(
        forecast=forecast_res,
        num_scenarios=50,
        horizon_hours=24,
        uncertainty_std=0.06,
        seed=42,
    )

    assert isinstance(mc_res, MonteCarloDemandScenarioResult)
    assert mc_res.horizon_hours == 24
    assert mc_res.num_scenarios == 50
    assert len(mc_res.timestamps) == 24
    assert len(mc_res.expected_forecast) == 24
    assert len(mc_res.scenario_curves) == 50

    # Verify scenario point validity
    for curve in mc_res.scenario_curves:
        assert len(curve) == 24
        for val in curve:
            assert isinstance(val, float)
            assert val >= 0.0, f"Encountered negative demand value: {val}"

    # Statistical consistency checks
    assert len(mc_res.mean_scenario_demand) == 24
    assert len(mc_res.min_scenario_demand) == 24
    assert len(mc_res.max_scenario_demand) == 24
    assert len(mc_res.std_dev) == 24

    for t in range(24):
        hour_vals = [c[t] for c in mc_res.scenario_curves]
        assert np.isclose(mc_res.mean_scenario_demand[t], np.mean(hour_vals), atol=1e-3)
        assert np.isclose(mc_res.min_scenario_demand[t], np.min(hour_vals), atol=1e-3)
        assert np.isclose(mc_res.max_scenario_demand[t], np.max(hour_vals), atol=1e-3)
        assert np.isclose(mc_res.std_dev[t], np.std(hour_vals), atol=1e-3)
        assert (
            mc_res.min_scenario_demand[t]
            <= mc_res.percentiles["p10"][t]
            <= mc_res.percentiles["p50"][t]
            <= mc_res.percentiles["p90"][t]
            <= mc_res.max_scenario_demand[t]
        )

    # Test serialization
    data = mc_res.to_dict()
    assert data["horizon_hours"] == 24
    assert data["num_scenarios"] == 50
    assert len(data["scenario_curves"]) == 50
    assert "mean_scenario_demand" in data
    assert "percentiles" in data


def test_monte_carlo_configurable_scenarios_and_uncertainty():
    """Verify Monte Carlo handles configurable scenario counts and uncertainty scales."""
    import numpy as np
    from ai.simulation import simulate_monte_carlo_demand_scenarios

    expected_curve = [35.0 + 5.0 * np.sin(i * np.pi / 12.0) for i in range(24)]

    # Low uncertainty
    res_low = simulate_monte_carlo_demand_scenarios(
        forecast=expected_curve,
        num_scenarios=20,
        horizon_hours=24,
        uncertainty_std=0.01,
        seed=42,
    )
    assert res_low.num_scenarios == 20
    assert len(res_low.scenario_curves) == 20

    # High uncertainty
    res_high = simulate_monte_carlo_demand_scenarios(
        forecast=expected_curve,
        num_scenarios=80,
        horizon_hours=24,
        uncertainty_std=0.15,
        seed=42,
    )
    assert res_high.num_scenarios == 80
    assert len(res_high.scenario_curves) == 80

    # Average standard deviation should be significantly higher for 15% uncertainty than 1%
    avg_std_low = np.mean(res_low.std_dev)
    avg_std_high = np.mean(res_high.std_dev)
    assert avg_std_high > avg_std_low * 5.0


def test_monte_carlo_reproducibility_with_seed():
    """Verify identical random seeds yield perfectly reproducible Monte Carlo trajectories."""
    import numpy as np
    from ai.simulation import simulate_monte_carlo_demand_scenarios

    expected_curve = [50.0] * 24

    res1 = simulate_monte_carlo_demand_scenarios(expected_curve, num_scenarios=30, seed=123)
    res2 = simulate_monte_carlo_demand_scenarios(expected_curve, num_scenarios=30, seed=123)
    res3 = simulate_monte_carlo_demand_scenarios(expected_curve, num_scenarios=30, seed=999)

    assert np.allclose(res1.scenario_curves, res2.scenario_curves)
    assert np.allclose(res1.mean_scenario_demand, res2.mean_scenario_demand)
    assert not np.allclose(res1.scenario_curves, res3.scenario_curves)

