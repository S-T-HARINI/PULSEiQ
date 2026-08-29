"""
PULSEiQ — AI/ML Integration Verification Test Suite.
Verifies AI/ML module importability, execution, schema compatibility with backend schemas,
backend-to-AI communication status, and error handling for invalid inputs.
"""

import json
import pytest
from datetime import datetime, timezone

# 1. AI/ML Module Imports
import ai
from ai.models.mock_grid import create_mock_grid
from ai.models.grid import ComponentStatus, CriticalityLevel, ElectricityGrid, NodeType, ScenarioConfig
from ai.forecasting import (
    DemandForecaster,
    GridForecaster,
    SolarForecaster,
    WindForecaster,
    ForecastResult,
    GridForecastSummary,
)
from ai.simulation import (
    SimulationResult,
    MonteCarloSummary,
    solve_power_flow,
    run_monte_carlo_simulation,
)
from ai.risk import (
    GridRiskAssessment,
    ContingencyResult,
    CascadingFailureReport,
    ComponentCriticality,
    ConnectivitySummary,
    RiskLevel,
    RiskThresholds,
    RiskWeightsConfig,
    analyze_n_k,
    run_n_1_analysis,
    run_n_k_analysis,
    rank_critical_components,
    simulate_cascading_failure,
    calculate_grid_risk_index,
)
from ai.graph import (
    GraphAnalysisResult,
    grid_to_networkx,
    get_topology_summary,
    identify_important_nodes,
    analyze_graph_topology,
    find_connected_components,
    find_isolated_load_nodes,
    find_articulation_points,
    find_bridges,
)
from ai.optimization import (
    DispatchResult,
    OptimizationConfig,
    OptimizationStatus,
    solve_optimal_dispatch,
)
from ai.pipeline import (
    GridIntelligencePipeline,
    GridAIPipeline,
    PipelineConfig,
    PipelineInput,
    GridIntelligenceResult,
    PipelineValidationError,
)

# 2. Backend Schemas & Bridge Imports (Optional guard for standalone AI branches)
try:
    from backend.app.core.ai_bridge import ai_bridge
    from backend.app.schemas.forecast import ForecastDataPoint, ForecastResponse, ForecastType
    from backend.app.schemas.simulation import SimulationRunResponse
    from backend.app.schemas.risk import AffectedComponent, CriticalLoadImpact, RiskAnalysisResponse, RiskLevel as BackendRiskLevel
    from backend.app.schemas.optimization import GeneratorDispatch, OptimizationObjective, OptimizationRunResponse
    BACKEND_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    BACKEND_AVAILABLE = False


def test_ai_modules_import_cleanly():
    """Verify that all core AI/ML modules and public APIs can be imported without errors."""
    assert ai.__version__ is not None
    assert callable(create_mock_grid)
    assert callable(solve_power_flow)
    assert callable(calculate_grid_risk_index)
    assert callable(grid_to_networkx)
    assert callable(solve_optimal_dispatch)
    assert callable(GridIntelligencePipeline)


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend schemas not available")
def test_ai_forecasting_execution_and_schema_compatibility():
    """Verify forecasting runs and produces data compatible with backend ForecastResponse."""
    grid = create_mock_grid()
    forecaster = GridForecaster()
    summary = forecaster.forecast_grid(grid, horizon_hours=24)

    assert isinstance(summary, GridForecastSummary)
    assert len(summary.total_demand_curve) == 24
    assert len(summary.total_renewable_curve) == 24
    assert len(summary.net_load_curve) == 24

    # Verify compatibility with backend.app.schemas.forecast.ForecastResponse
    data_points = [
        ForecastDataPoint(
            timestamp=summary.timestamps[i],
            predicted_demand_mw=summary.total_demand_curve[i],
            predicted_renewable_mw=summary.total_renewable_curve[i],
            value_mw=summary.total_demand_curve[i],
            lower_bound_mw=round(summary.total_demand_curve[i] * 0.90, 2),
            upper_bound_mw=round(summary.total_demand_curve[i] * 1.10, 2),
        )
        for i in range(24)
    ]
    vals = [p.value_mw for p in data_points]

    backend_response = ForecastResponse(
        forecast_type=ForecastType.LOAD,
        horizon_hours=24,
        values=data_points,
        peak_mw=max(vals),
        min_mw=min(vals),
        average_mw=sum(vals) / len(vals),
        confidence_score=0.95,
        model_source="ai_module",
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    assert backend_response.horizon_hours == 24
    assert len(backend_response.values) == 24
    assert backend_response.model_source == "ai_module"


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend schemas not available")
def test_ai_simulation_execution_and_schema_compatibility():
    """Verify physical simulation runs and produces data compatible with backend SimulationRunResponse."""
    grid = create_mock_grid()
    sim_res = solve_power_flow(grid)

    assert isinstance(sim_res, SimulationResult)
    assert sim_res.total_generation_mw > 0
    assert sim_res.total_demand_mw > 0
    assert 59.0 <= sim_res.frequency_hz <= 61.0

    # Verify compatibility with backend.app.schemas.simulation.SimulationRunResponse
    backend_sim_response = SimulationRunResponse(
        simulation_status="completed",
        total_generation_mw=sim_res.total_generation_mw,
        total_demand_mw=sim_res.total_demand_mw,
        renewable_generation_mw=grid.total_renewable_generation_mw,
        line_utilization_avg=sum(l.utilization_pct for l in sim_res.line_results.values()) / max(len(sim_res.line_results), 1),
        line_loading={lid: round(l.utilization_pct, 2) for lid, l in sim_res.line_results.items()},
        frequency_hz=round(sim_res.frequency_hz, 3),
        voltage_indicators={
            "min_voltage_pu": min(b.voltage_pu for b in sim_res.bus_voltages.values()),
            "max_voltage_pu": max(b.voltage_pu for b in sim_res.bus_voltages.values()),
            "avg_voltage_pu": sum(b.voltage_pu for b in sim_res.bus_voltages.values()) / max(len(sim_res.bus_voltages), 1),
        },
        simulation_warnings=[],
        affected_components=[],
        risk_index=0.14,
        resulting_grid_state=None,
        model_source="ai_module",
        timestamp=datetime.now(timezone.utc).isoformat(),
        details={"solver": "DC-PowerFlow", "is_frequency_stable": sim_res.is_frequency_stable},
    )
    assert backend_sim_response.simulation_status == "completed"
    assert backend_sim_response.total_generation_mw == sim_res.total_generation_mw


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend schemas not available")
def test_ai_risk_execution_and_schema_compatibility():
    """Verify risk analysis runs and produces data compatible with backend RiskAnalysisResponse."""
    grid = create_mock_grid()
    risk_assessment = calculate_grid_risk_index(grid)

    assert isinstance(risk_assessment, GridRiskAssessment)
    assert 0.0 <= risk_assessment.risk_index <= 1.0
    assert risk_assessment.risk_level in (RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL)

    # Verify compatibility with backend.app.schemas.risk.RiskAnalysisResponse
    vuln_components = [
        AffectedComponent(
            id=c.component_id,
            name=c.component_name,
            type=c.component_type,
            impact="critical_vulnerability" if c.is_articulation_point or c.is_bridge else "monitored",
            utilization_or_loading=c.utilization_pct,
        )
        for c in risk_assessment.ranked_critical_components
    ]

    crit_impact = CriticalLoadImpact(
        critical_load_at_risk=risk_assessment.critical_load_at_risk,
        critical_load_at_risk_mw=26.5 if risk_assessment.critical_load_at_risk else 0.0,
        affected_critical_facilities=["St. Jude Regional Trauma Center & Hospital", "Metro Tier-IV Cloud Data Center"] if risk_assessment.critical_load_at_risk else [],
    )

    backend_risk_response = RiskAnalysisResponse(
        risk_index=risk_assessment.risk_index,
        risk_level=BackendRiskLevel(risk_assessment.risk_level.value.lower()),
        vulnerable_components=vuln_components,
        affected_components=vuln_components,
        critical_load_impact=crit_impact,
        contingency_results={"total_screened": len(risk_assessment.most_critical_contingencies)},
        n1_analysis={"n1_violations_count": risk_assessment.n_1_violations_count},
        cascading_failure_indicators={"cascading_risk_score": risk_assessment.cascading_risk_score},
        model_source="ai_module",
        explanation="Evaluated via Person 3 Multi-Factor Risk Model",
        summary=risk_assessment.summary,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )
    assert backend_risk_response.risk_index == risk_assessment.risk_index
    assert backend_risk_response.model_source == "ai_module"


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend schemas not available")
def test_ai_optimization_execution_and_schema_compatibility():
    """Verify optimization solver runs and produces data compatible with backend OptimizationRunResponse."""
    grid = create_mock_grid()
    opt_res = solve_optimal_dispatch(grid)

    assert isinstance(opt_res, DispatchResult)
    assert opt_res.status == OptimizationStatus.OPTIMAL
    assert opt_res.total_generation_dispatched_mw > 0

    # Verify compatibility with backend.app.schemas.optimization.OptimizationRunResponse
    dispatches = [
        GeneratorDispatch(
            generator_id=gid,
            generator_name=grid.nodes[gid].name if gid in grid.nodes else gid,
            type=grid.nodes[gid].node_type.value if gid in grid.nodes else "generator",
            dispatched_mw=mw,
            capacity_mw=grid.nodes[gid].operational.max_capacity_mw if gid in grid.nodes else mw,
            marginal_cost_per_mwh=30.0,
        )
        for gid, mw in opt_res.generator_dispatch_mw.items()
    ]

    bat_mw = sum(opt_res.battery_dispatch_mw.values()) if opt_res.battery_dispatch_mw else 0.0

    backend_opt_response = OptimizationRunResponse(
        optimization_status="optimal",
        objective=OptimizationObjective.COST_MINIMIZATION,
        recommended_actions=[
            "Dispatch zero-marginal-cost renewable assets first.",
            "Schedule BESS discharging to cover peak net demand.",
        ],
        generator_dispatch=dispatches,
        total_dispatched_generation_mw=opt_res.total_generation_dispatched_mw,
        battery_dispatch_mw=bat_mw,
        battery_charge_discharge_mw=bat_mw,
        backup_generation_mw=0.0,
        flexible_load_reduction_mw=0.0,
        renewable_curtailment_mw=sum(opt_res.curtailed_renewable_mw.values()),
        unserved_demand_mw=sum(opt_res.unserved_demand_mw.values()),
        expected_risk_reduction=0.18,
        objective_value=opt_res.total_cost,
        cost_estimate_usd=opt_res.total_cost,
        model_source="ai_module",
        summary=opt_res.summary,
        solved_at=datetime.now(timezone.utc).isoformat(),
    )
    assert backend_opt_response.optimization_status == "optimal"
    assert backend_opt_response.total_dispatched_generation_mw == opt_res.total_generation_dispatched_mw


def test_ai_graph_execution():
    """Verify NetworkX graph construction and topology analytics."""
    grid = create_mock_grid()
    G = grid_to_networkx(grid)
    analysis = analyze_graph_topology(G, grid=grid)

    assert isinstance(analysis, GraphAnalysisResult)
    assert analysis.node_count == 12
    assert analysis.edge_count == 12
    assert analysis.is_connected is True
    assert len(analysis.articulation_points) > 0
    assert len(analysis.bridges) > 0


def test_ai_pipeline_execution():
    """Verify end-to-end GridIntelligencePipeline execution."""
    grid = create_mock_grid()
    pipeline = GridIntelligencePipeline()
    result = pipeline.run(grid)

    assert isinstance(result, GridIntelligenceResult)
    assert result.status == "SUCCESS"
    assert result.forecast.horizon_hours == 24
    assert 0.0 <= result.risk.score <= 1.0
    assert result.topology.node_count == 12
    assert result.simulation.power_flow_converged is True

    # Test serialization to JSON
    json_str = json.dumps(result.to_dict())
    assert len(json_str) > 0


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend bridge not available")
def test_backend_ai_bridge_audit():
    """
    Audits the actual connection state between the backend AI bridge and Person 3 AI modules.
    Identifies that modules are dynamically detected, but function signature delegation
    currently triggers the graceful fallback handler.
    """
    # 1. AI Modules are successfully imported and discovered
    assert ai_bridge.is_forecasting_available() is True
    assert ai_bridge.is_simulation_available() is True
    assert ai_bridge.is_risk_available() is True
    assert ai_bridge.is_optimization_available() is True

    # 2. Status summary reflects detection
    summary = ai_bridge.get_status_summary()
    assert summary["forecasting"] == "ai_module_connected"
    assert summary["simulation"] == "ai_module_connected"
    assert summary["risk_engine"] == "ai_module_connected"
    assert summary["optimization"] == "ai_module_connected"

    # 3. Invocation audit: run_ai_* methods return None because bridge calls
    # methods like 'predict', 'simulate', 'analyze', 'optimize' which are not top-level functions on ai.*
    fc_res = ai_bridge.run_ai_forecast(forecast_type="load", horizon_hours=24)
    assert fc_res is None  # Triggers service_fallback in backend

    sim_res = ai_bridge.run_ai_simulation(scenario_id="test")
    assert sim_res is None  # Triggers service_fallback in backend

    risk_res = ai_bridge.run_ai_risk_analysis(contingency_type="N-1")
    assert risk_res is None  # Triggers service_fallback in backend

    opt_res = ai_bridge.run_ai_optimization(objective="cost_minimization")
    assert opt_res is None  # Triggers service_fallback in backend


def test_invalid_input_validation():
    """Verify error handling on invalid inputs across AI modules."""
    pipeline = GridIntelligencePipeline()

    # None input
    with pytest.raises(PipelineValidationError, match="Expected ElectricityGrid or PipelineInput"):
        pipeline.run(None)

    # Empty grid
    empty_grid = ElectricityGrid(grid_id="empty", name="Empty")
    with pytest.raises(PipelineValidationError, match="contains no nodes"):
        pipeline.run(empty_grid)

    # Negative horizon
    grid = create_mock_grid()
    with pytest.raises(PipelineValidationError, match="forecast_horizon_hours must be a positive integer"):
        pipeline.run(grid, config=PipelineConfig(forecast_horizon_hours=-5))
