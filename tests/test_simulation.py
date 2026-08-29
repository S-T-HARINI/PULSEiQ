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
