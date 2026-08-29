"""
Unit tests for PULSEiQ Contingency, Cascading Failure, Critical Component Ranking, and Risk Scoring Module.
"""

import pytest
from ai.models.grid import ComponentStatus, CriticalityLevel, ElectricityGrid, ScenarioConfig
from ai.models.mock_grid import create_mock_grid
from ai.risk import (
    ContingencyType,
    RiskLevel,
    RiskThresholds,
    RiskWeightsConfig,
    analyze_n_k,
    calculate_grid_risk_index,
    evaluate_contingency,
    rank_critical_components,
    run_n_1_analysis,
    run_n_k_analysis,
    simulate_cascading_failure,
)


def test_risk_score_calculation():
    """Verify multi-factor risk index calculation and threshold mappings."""
    grid = create_mock_grid()

    assessment = calculate_grid_risk_index(grid)
    assert 0.0 <= assessment.risk_index <= 1.0
    assert assessment.risk_level in (RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert "n1_contingency_insecurity" in assessment.risk_factors
    assert "transmission_loading" in assessment.risk_factors
    assert "critical_load_exposure" in assessment.risk_factors
    assert "generation_reserve_risk" in assessment.risk_factors
    assert "renewable_variability" in assessment.risk_factors
    assert "battery_storage_risk" in assessment.risk_factors
    assert "voltage_frequency_deviation" in assessment.risk_factors

    # Test RiskThresholds mapping
    assert RiskThresholds.get_risk_level(0.10) == RiskLevel.LOW
    assert RiskThresholds.get_risk_level(0.35) == RiskLevel.MODERATE
    assert RiskThresholds.get_risk_level(0.60) == RiskLevel.HIGH
    assert RiskThresholds.get_risk_level(0.85) == RiskLevel.CRITICAL

    # Test custom weights configuration
    custom_weights = RiskWeightsConfig(
        n1_vulnerability_weight=0.50,
        critical_load_exposure_weight=0.30,
        line_loading_weight=0.20,
    )
    custom_assessment = calculate_grid_risk_index(grid, config=custom_weights)
    assert 0.0 <= custom_assessment.risk_index <= 1.0


def test_n_1_line_outages():
    """Verify N-1 line outages: component removed, remaining connectivity, overloaded components, and severity."""
    grid = create_mock_grid()
    n1_results = run_n_1_analysis(grid, top_n_worst=0)  # Evaluate all single outages

    assert len(n1_results) >= len(grid.lines)

    # Line outage test on main transmission trunk
    trunk_outage = next((r for r in n1_results if "line_submain_to_subsouth" in r.tripped_components), None)
    assert trunk_outage is not None
    assert trunk_outage.contingency_type == ContingencyType.N_MINUS_1_LINE
    assert trunk_outage.tripped_components == ["line_submain_to_subsouth"]
    assert isinstance(trunk_outage.is_grid_operational, bool)
    assert isinstance(trunk_outage.connectivity.is_connected, bool)
    assert len(trunk_outage.affected_components) >= 1
    assert trunk_outage.severity in ("LOW", "MODERATE", "HIGH", "CRITICAL")


def test_n_1_generator_outages():
    """Verify N-1 generator outages: gas CCGT, solar PV, and wind farms."""
    grid = create_mock_grid()

    # Outage of main gas plant
    gas_outage = analyze_n_k(
        grid=grid,
        failed_components=["gen_gas_01"],
        contingency_type=ContingencyType.N_MINUS_1_GEN,
    )

    assert gas_outage.tripped_components == ["gen_gas_01"]
    assert gas_outage.contingency_type == ContingencyType.N_MINUS_1_GEN
    # Gas outage removes 75MW out of 135MW generation, resulting in generation deficit
    assert gas_outage.critical_load_at_risk is True
    assert gas_outage.severity in ("MODERATE", "HIGH", "CRITICAL")
    assert gas_outage.risk_score > 40.0


def test_n_k_contingency_analysis():
    """Verify N-k multi-asset outage evaluation."""
    grid = create_mock_grid()

    # 1. Custom N-2 failure (Gas plant + North trunk line)
    n2_res = analyze_n_k(
        grid=grid,
        failed_components=["gen_gas_01", "line_submain_to_subnorth"],
        contingency_type=ContingencyType.N_MINUS_K,
    )

    assert len(n2_res.tripped_components) == 2
    assert "gen_gas_01" in n2_res.tripped_components
    assert "line_submain_to_subnorth" in n2_res.tripped_components
    assert n2_res.is_secure is False
    assert n2_res.risk_score > 50.0

    # 2. Automated N-2 screening
    nk_screen = run_n_k_analysis(grid, k=2, max_combinations=10)
    assert len(nk_screen) == 10
    for res in nk_screen:
        assert len(res.tripped_components) == 2
        assert res.contingency_type == ContingencyType.N_MINUS_K


def test_critical_component_ranking():
    """Verify dynamic ranking of components by vulnerability and importance."""
    grid = create_mock_grid()
    ranked = rank_critical_components(grid, top_n=8)

    assert len(ranked) == 8
    # Verify ranking order (rank 1 has highest or equal risk score)
    for i in range(len(ranked) - 1):
        assert ranked[i].risk_score >= ranked[i + 1].risk_score
        assert ranked[i].overall_criticality_rank == i + 1

    # Main bulk transmission substation must rank near top due to articulation point & high connectivity
    top_ids = [c.component_id for c in ranked[:3]]
    assert "sub_trans_main" in top_ids

    # Check serialization
    first = ranked[0].to_dict()
    assert "component_id" in first
    assert "centrality_score" in first
    assert "critical_load_exposure_mw" in first
    assert "overall_criticality_rank" in first


def test_cascading_failure_simulation():
    """Verify multi-stage cascading failure progression with initial, secondary, and final states."""
    grid = create_mock_grid()

    # Initiate cascading outage from South trunk line
    cascade = simulate_cascading_failure(grid, initial_trips=["line_submain_to_subsouth"])

    assert cascade.initiating_contingency == ["line_submain_to_subsouth"]
    assert cascade.initial_failure == ["line_submain_to_subsouth"]
    assert isinstance(cascade.secondary_failures, list)
    assert cascade.total_stages >= 1
    assert len(cascade.stages) == cascade.total_stages
    assert "is_stable" in cascade.final_state
    assert "blackout_occurred" in cascade.final_state
    assert 0.0 <= cascade.cascade_risk_score <= 100.0


def test_error_handling():
    """Verify robust error handling on invalid inputs."""
    grid = create_mock_grid()

    # 1. Invalid component ID in analyze_n_k
    with pytest.raises(ValueError, match="Unknown failed component ID 'invalid_id_999'"):
        analyze_n_k(grid, failed_components=["invalid_id_999"])

    # 2. Invalid initial trips in cascading failure
    with pytest.raises(ValueError, match="Unknown initial trip ID 'fake_line'"):
        simulate_cascading_failure(grid, initial_trips=["fake_line"])

    # 3. Empty grid error handling
    empty_grid = ElectricityGrid(grid_id="empty", name="Empty")
    with pytest.raises(ValueError, match="empty or None"):
        analyze_n_k(empty_grid, failed_components=[])

    with pytest.raises(ValueError, match="empty or None"):
        calculate_grid_risk_index(empty_grid)

    with pytest.raises(ValueError, match="empty or None"):
        rank_critical_components(empty_grid)
