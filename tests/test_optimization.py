"""
Unit tests for PULSEiQ Optimal Dispatch & Storage Scheduling Module.
"""

import pytest
from ai.models.grid import ScenarioConfig
from ai.models.mock_grid import create_mock_grid
from ai.optimization import (
    OptimizationConfig,
    OptimizationStatus,
    solve_optimal_dispatch,
)


def test_solve_optimal_dispatch_baseline():
    """Verify economic power dispatch finds optimal generation dispatch without unserved load."""
    grid = create_mock_grid()
    res = solve_optimal_dispatch(grid)

    assert res.status == OptimizationStatus.OPTIMAL
    assert res.total_cost > 0.0
    assert res.total_demand_served_mw > 100.0
    assert res.critical_unserved_mw == 0.0
    assert res.critical_load_served_pct == 100.0

    # Gas, Solar, and Wind dispatches are positive
    assert "gen_gas_01" in res.generator_dispatch_mw
    assert res.generator_dispatch_mw["gen_gas_01"] > 0
    assert "solar_farm_01" in res.generator_dispatch_mw
    assert "wind_farm_01" in res.generator_dispatch_mw

    # Battery state of charge tracked
    assert "bess_storage_01" in res.battery_soc_after_pct
    assert 0.0 <= res.battery_soc_after_pct["bess_storage_01"] <= 100.0

    # Serialization test
    data = res.to_dict()
    assert data["status"] == "OPTIMAL"
    assert "total_cost" in data
    assert "critical_load_served_pct" in data


def test_priority_critical_load_protection():
    """Verify that during extreme generation deficit, normal loads are shed first, protecting critical loads."""
    grid = create_mock_grid()

    # Extreme scenario: trip large gas plant and disable solar/wind
    contingency_grid = grid.apply_scenario(
        ScenarioConfig(
            solar_multiplier=0.0,
            wind_multiplier=0.0,
            contingencies=["gen_gas_01"],
        )
    )

    res = solve_optimal_dispatch(contingency_grid)

    assert res.status == OptimizationStatus.OPTIMAL
    # Total generation + BESS cannot meet total demand, so load shedding is required
    normal_unserved = sum(
        val for nid, val in res.unserved_demand_mw.items()
        if not grid.get_node(nid).is_critical
    )
    assert normal_unserved > 0.0
    # Hospital and Data Center (critical loads) are 100% protected
    assert res.critical_unserved_mw == 0.0
    assert res.critical_load_served_pct == 100.0
