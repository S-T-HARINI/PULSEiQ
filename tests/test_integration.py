"""
PULSEiQ — Real AI/ML ↔ Backend Integration Test Suite.
PROVES that backend services and endpoints directly invoke the real Person 3 AI/ML engines
(Forecasting, Risk Analysis, Simulation, Optimization, Graph Analytics, Unified Pipeline)
and verify deterministic fallback behavior when the AI engine is offline.
"""

import json
from unittest.mock import patch
import pytest
from starlette.testclient import TestClient

# 1. Real AI/ML Module Imports
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
    analyze_graph_topology,
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

# 2. Backend Schemas, Bridge & App Imports
try:
    from backend.app.main import app
    from backend.app.core.ai_bridge import ai_bridge
    from backend.app.services.grid_service import grid_service
    from backend.app.schemas.forecast import ForecastDataPoint, ForecastResponse, ForecastType
    from backend.app.schemas.simulation import SimulationRunRequest, SimulationRunResponse
    from backend.app.schemas.risk import AffectedComponent, CriticalLoadImpact, RiskAnalysisRequest, RiskAnalysisResponse, RiskLevel as BackendRiskLevel
    from backend.app.schemas.optimization import GeneratorDispatch, OptimizationObjective, OptimizationRunRequest, OptimizationRunResponse
    BACKEND_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    BACKEND_AVAILABLE = False


@pytest.fixture
def client():
    if not BACKEND_AVAILABLE:
        pytest.skip("Backend not available")
    return TestClient(app)


# =============================================================================
# 1. AI/ML MODULE INTEGRITY & DIRECT EXECUTION TESTS
# =============================================================================

def test_ai_modules_import_cleanly():
    """Verify all core AI/ML algorithms and data models import cleanly."""
    assert ai.__version__ is not None
    assert callable(create_mock_grid)
    assert callable(solve_power_flow)
    assert callable(calculate_grid_risk_index)
    assert callable(grid_to_networkx)
    assert callable(solve_optimal_dispatch)
    assert callable(GridIntelligencePipeline)


def test_ai_graph_execution():
    """Verify NetworkX graph construction and topology metrics."""
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
    assert result.simulation.power_flow_converged is True

    # JSON serialization roundtrip
    json_str = json.dumps(result.to_dict())
    assert len(json_str) > 0


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


# =============================================================================
# 2. REAL AI ↔ BACKEND DIRECT BRIDGE & EXECUTION TESTS
# =============================================================================

@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend not available")
def test_backend_ai_bridge_real_execution():
    """
    PROVES that ai_bridge calls the REAL AI/ML implementations and returns
    structured results with model_source='ai_module'.
    """
    # 1. Operational status
    assert ai_bridge.is_forecasting_available() is True
    assert ai_bridge.is_simulation_available() is True
    assert ai_bridge.is_risk_available() is True
    assert ai_bridge.is_optimization_available() is True
    assert ai_bridge.is_graph_available() is True
    assert ai_bridge.is_pipeline_available() is True

    summary = ai_bridge.get_status_summary()
    assert summary["forecasting"] == "ai_module_connected"
    assert summary["simulation"] == "ai_module_connected"
    assert summary["risk_engine"] == "ai_module_connected"
    assert summary["optimization"] == "ai_module_connected"

    # 2. Real AI Forecasting via Bridge
    fc_res = ai_bridge.run_ai_forecast(forecast_type="load", horizon_hours=24)
    assert fc_res is not None
    assert fc_res["model_source"] == "ai_module"
    assert len(fc_res["values"]) == 24
    assert fc_res["confidence_score"] >= 0.90

    # 3. Real AI Simulation via Bridge (DC Power Flow)
    sim_res = ai_bridge.run_ai_simulation(duration_hours=24)
    assert sim_res is not None
    assert sim_res["model_source"] == "ai_module"
    assert sim_res["simulation_status"] == "completed"
    assert sim_res["total_generation_mw"] > 0
    assert 49.9 <= sim_res["frequency_hz"] <= 50.1

    # 4. Real AI Risk Analysis via Bridge (Multi-Factor & N-1)
    risk_res = ai_bridge.run_ai_risk_analysis(contingency_type="N-1", failed_component_id="line-north-central-1")
    assert risk_res is not None
    assert risk_res["model_source"] == "ai_module"
    assert 0.0 <= risk_res["risk_index"] <= 1.0
    assert len(risk_res["vulnerable_components"]) > 0

    # 5. Real AI Optimization via Bridge (solve_optimal_dispatch)
    opt_res = ai_bridge.run_ai_optimization(objective="cost_minimization")
    assert opt_res is not None
    assert opt_res["model_source"] == "ai_module"
    assert opt_res["optimization_status"] == "optimal"
    assert len(opt_res["generator_dispatch"]) > 0

    # 6. Real AI Graph Analysis via Bridge
    graph_res = ai_bridge.run_ai_graph_analysis()
    assert graph_res is not None
    assert graph_res["node_count"] == 50  # Backend grid has 50 nodes
    assert graph_res["edge_count"] >= 40  # Backend grid has 40+ lines
    assert "articulation_points" in graph_res

    # 7. Real AI Unified Pipeline via Bridge
    pipeline_res = ai_bridge.run_ai_pipeline()
    assert pipeline_res is not None
    assert pipeline_res["status"] == "SUCCESS"
    assert "forecast" in pipeline_res
    assert "risk" in pipeline_res
    assert "simulation" in pipeline_res


# =============================================================================
# 3. ENDPOINT INTEGRATION TESTS (PROVING REAL AI CALLS VIA FASTAPI API)
# =============================================================================

@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend not available")
def test_forecast_api_calls_real_ai(client):
    """PROVES POST /api/v1/forecast executes the real AI forecasting engine."""
    payload = {
        "forecast_type": "load",
        "horizon_hours": 24,
        "historical_demand_mw": [420.0, 430.0, 445.0, 460.0],
        "weather_info": {"temperature_c": 29.5, "solar_irradiance": 820.0},
    }
    response = client.post("/api/v1/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["model_source"] == "ai_module", "Must identify real AI execution"
    assert len(data["values"]) == 24
    assert data["peak_mw"] >= data["min_mw"]
    assert data["confidence_score"] >= 0.90


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend not available")
def test_simulation_api_calls_real_ai(client):
    """PROVES POST /api/v1/simulation executes the real DC power-flow AI simulation."""
    payload = {
        "scenario_id": "integration_sim_01",
        "duration_hours": 24,
        "time_step_minutes": 60,
        "load_growth_factor": 1.10,
        "contingency_event": "line-north-central-1",
    }
    response = client.post("/api/v1/simulation", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["model_source"] == "ai_module", "Must identify real AI execution"
    assert data["simulation_status"] == "completed"
    assert data["total_generation_mw"] > 0
    assert 49.9 <= data["frequency_hz"] <= 50.1
    assert len(data["line_loading"]) > 0


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend not available")
def test_risk_api_calls_real_ai(client):
    """PROVES POST /api/v1/risk executes the real multi-factor AI risk assessment."""
    payload = {
        "contingency_type": "N-1",
        "failed_component_id": "line-north-central-1",
        "monte_carlo_iterations": 1000,
    }
    response = client.post("/api/v1/risk", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["model_source"] == "ai_module", "Must identify real AI execution"
    assert data["risk_level"] in ["low", "moderate", "high", "critical"]
    assert len(data["vulnerable_components"]) > 0
    assert "contingency_results" in data


@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend not available")
def test_optimization_api_calls_real_ai(client):
    """PROVES POST /api/v1/optimization executes the real HiGHS LP solver."""
    payload = {
        "objective": "cost_minimization",
        "demand_mw": 460.0,
        "battery_availability": {"soc_percent": 78.5, "capacity_mw": 80.0},
    }
    response = client.post("/api/v1/optimization", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["model_source"] == "ai_module", "Must identify real AI execution"
    assert data["optimization_status"] == "optimal"
    assert len(data["generator_dispatch"]) > 0
    assert data["cost_estimate_usd"] > 0


# =============================================================================
# 4. RESILIENCE & OBSERVABLE FALLBACK VERIFICATION
# =============================================================================

@pytest.mark.skipif(not BACKEND_AVAILABLE, reason="Backend not available")
def test_forced_ai_failure_activates_observable_fallback(client):
    """
    PROVES that when the AI engine encounters a forced failure, the backend:
    1. Catches the error gracefully without crashing.
    2. Uses fallback calculations for resilience.
    3. Explicitly labels model_source='service_fallback' (never claiming it is AI).
    """
    # 1. Force AI forecasting failure
    with patch.object(ai_bridge, "run_ai_forecast", return_value=None):
        payload = {"forecast_type": "load", "horizon_hours": 24}
        response = client.post("/api/v1/forecast", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["model_source"] == "service_fallback", "Fallback must be explicitly identified"
        assert len(data["values"]) == 24

    # 2. Force AI simulation failure
    with patch.object(ai_bridge, "run_ai_simulation", return_value=None):
        payload = {"scenario_id": "test_fallback_sim"}
        response = client.post("/api/v1/simulation", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["model_source"] == "service_fallback", "Fallback must be explicitly identified"

    # 3. Force AI risk engine failure
    with patch.object(ai_bridge, "run_ai_risk_analysis", return_value=None):
        payload = {"contingency_type": "N-1", "failed_component_id": "line-north-central-1"}
        response = client.post("/api/v1/risk", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["model_source"] == "service_fallback", "Fallback must be explicitly identified"

    # 4. Force AI optimization solver failure
    with patch.object(ai_bridge, "run_ai_optimization", return_value=None):
        payload = {"objective": "cost_minimization", "demand_mw": 460.0}
        response = client.post("/api/v1/optimization", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["model_source"] == "service_fallback", "Fallback must be explicitly identified"
