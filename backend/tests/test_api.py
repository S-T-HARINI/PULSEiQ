import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.grid import (
    GridResponse,
    NodeType,
    NodeStatus,
    NodeCriticality,
    EdgeStatus,
)
from backend.app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
)
from backend.app.schemas.forecast import (
    ForecastType,
    ForecastRequest,
    ForecastResponse,
)
from backend.app.schemas.risk import (
    RiskLevel,
    RiskAnalysisRequest,
    RiskAnalysisResponse,
)
from backend.app.schemas.optimization import (
    OptimizationObjective,
    OptimizationRunRequest,
    OptimizationRunResponse,
)
from backend.app.schemas.scenario import (
    ScenarioType,
    ScenarioWhatIfRequest,
    ScenarioWhatIfResponse,
)


@pytest.fixture
def client():
    return TestClient(app)


# 1. Health Endpoint Test
def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "PULSEiQ Backend"
    assert data["version"] == "1.0.0"


# 2. Root Endpoint Test
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "PULSEiQ Backend"
    assert data["status"] == "operational"
    assert data["health_check"] == "/api/v1/health"
    assert data["grid_state"] == "/api/v1/grid"


# 3. GET /api/v1/grid Data & Schema Validation Test
def test_get_grid_endpoint(client):
    response = client.get("/api/v1/grid")
    assert response.status_code == 200
    data = response.json()

    # Validate with Pydantic model
    grid_model = GridResponse(**data)
    assert len(grid_model.nodes) == 11
    assert len(grid_model.edges) == 10

    # Verify node types present in grid
    node_types = {n.type for n in grid_model.nodes}
    assert NodeType.CONVENTIONAL_GENERATOR in node_types
    assert NodeType.SOLAR_PLANT in node_types
    assert NodeType.WIND_PLANT in node_types
    assert NodeType.BATTERY in node_types
    assert NodeType.SUBSTATION in node_types
    assert NodeType.LOAD in node_types
    assert NodeType.CRITICAL_LOAD in node_types

    # Verify critical load (hospital)
    hospital = next((n for n in grid_model.nodes if n.type == NodeType.CRITICAL_LOAD), None)
    assert hospital is not None
    assert hospital.criticality == NodeCriticality.CRITICAL
    assert hospital.current_output_mw == 45.0

    # Verify summary metrics
    summary = grid_model.summary
    assert summary.total_generation_mw == 475.0
    assert summary.total_demand_mw == 460.0
    assert summary.renewable_percentage > 0
    assert summary.battery_soc == 78.5
    assert 0.0 <= summary.grid_risk_index <= 1.0


# 4. Simulation Run Endpoint Test (POST /api/v1/simulation/run)
def test_simulation_run_endpoint(client):
    payload = {
        "scenario_id": "test_sim_01",
        "duration_hours": 24,
        "time_step_minutes": 60,
        "load_growth_factor": 1.15,
        "contingency_event": "line-north-central-1",
    }
    response = client.post("/api/v1/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    sim_resp = SimulationRunResponse(**data)
    assert sim_resp.simulation_status == "completed"
    assert sim_resp.total_generation_mw > 0
    assert sim_resp.total_demand_mw > 0
    assert sim_resp.renewable_generation_mw > 0
    assert sim_resp.line_utilization_avg > 0
    assert 48.0 <= sim_resp.frequency_hz <= 52.0
    assert "min_voltage_pu" in sim_resp.voltage_indicators
    assert 0.0 <= sim_resp.risk_index <= 1.0


# 5. Forecast Endpoint Tests (POST /api/v1/forecast)
@pytest.mark.parametrize("forecast_type", [
    ForecastType.LOAD,
    ForecastType.SOLAR,
    ForecastType.WIND,
])
def test_forecast_endpoint(client, forecast_type):
    payload = {
        "forecast_type": forecast_type.value,
        "horizon_hours": 24,
    }
    response = client.post("/api/v1/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()

    fc_resp = ForecastResponse(**data)
    assert fc_resp.forecast_type == forecast_type
    assert fc_resp.horizon_hours == 24
    assert len(fc_resp.values) == 24
    assert fc_resp.peak_mw >= fc_resp.min_mw
    assert fc_resp.average_mw > 0 or (forecast_type == ForecastType.SOLAR and fc_resp.average_mw >= 0)


# 6. Risk Analysis Endpoint Test (POST /api/v1/risk/analyze)
def test_risk_analysis_endpoint(client):
    payload = {
        "contingency_type": "N-1",
        "failed_component_id": "line-north-central-1",
        "monte_carlo_iterations": 1500,
    }
    response = client.post("/api/v1/risk/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    risk_resp = RiskAnalysisResponse(**data)
    assert risk_resp.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert len(risk_resp.affected_components) > 0
    assert "overload_propagation_probability" in risk_resp.cascading_failure_indicators
    assert len(risk_resp.explanation) > 0


# 7. Risk Analysis for Critical Hospital Threat
def test_risk_analysis_critical_load_threat(client):
    payload = {
        "contingency_type": "N-1",
        "failed_component_id": "line-south-to-hospital",
    }
    response = client.post("/api/v1/risk/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    risk_resp = RiskAnalysisResponse(**data)
    assert risk_resp.critical_load_at_risk is True
    assert risk_resp.critical_load_at_risk_mw == 45.0
    assert risk_resp.risk_level == RiskLevel.CRITICAL


# 8. Optimization Run Endpoint Test (POST /api/v1/optimization/run)
@pytest.mark.parametrize("objective", [
    OptimizationObjective.COST_MINIMIZATION,
    OptimizationObjective.EMISSION_REDUCTION,
    OptimizationObjective.RELIABILITY_MAXIMIZATION,
])
def test_optimization_run_endpoint(client, objective):
    payload = {
        "objective": objective.value,
        "demand_mw": 460.0,
        "battery_state": {"soc_percent": 78.5, "capacity_mw": 80.0},
    }
    response = client.post("/api/v1/optimization/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    opt_resp = OptimizationRunResponse(**data)
    assert opt_resp.optimization_status == "optimal"
    assert opt_resp.objective == objective
    assert len(opt_resp.generator_dispatch) == 3
    assert opt_resp.total_dispatched_generation_mw > 0
    assert opt_resp.cost_estimate_usd > 0


# 9. What-If Scenario Endpoint Tests (POST /api/v1/scenarios/what-if)
@pytest.mark.parametrize("scenario_type", [
    ScenarioType.EXTREME_HEATWAVE,
    ScenarioType.SOLAR_RAMP_DOWN,
    ScenarioType.N1_LINE_TRIP,
    ScenarioType.WIND_STORM,
])
def test_what_if_scenarios(client, scenario_type):
    payload = {
        "scenario_type": scenario_type.value,
        "name": f"Test {scenario_type.value}",
        "demand_multiplier": 1.25,
        "battery_available": True,
    }
    response = client.post("/api/v1/scenarios/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()

    scen_resp = ScenarioWhatIfResponse(**data)
    assert scen_resp.scenario_type == scenario_type
    assert scen_resp.generation_mw > 0
    assert scen_resp.demand_mw > 0
    assert 0.0 <= scen_resp.risk_index <= 1.0
    assert 0.0 <= scen_resp.critical_load_reliability_percent <= 100.0


# 10. Invalid Scenario Type Handled (422)
def test_invalid_scenario_type_rejected(client):
    payload = {"scenario_type": "alien_invasion_surge"}
    response = client.post("/api/v1/scenarios/what-if", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "Unprocessable Entity"


# 11. Invalid Component ID Handled (404)
def test_invalid_component_id_rejected(client):
    payload = {
        "scenario_type": "n1_line_trip",
        "failed_component_id": "nonexistent_substation_999",
    }
    response = client.post("/api/v1/scenarios/what-if", json=payload)
    assert response.status_code == 404
    assert "not found in grid topology" in response.json()["detail"]


# 12. Real-Time Telemetry WebSocket Test (/api/v1/ws/telemetry)
def test_websocket_telemetry(client):
    with client.websocket_connect("/api/v1/ws/telemetry") as ws:
        frame = ws.receive_json()
        assert "frequency" in frame
        assert "total_generation_mw" in frame
        assert "total_demand_mw" in frame
        assert "risk_index" in frame
        assert frame["status"] == "connected"

        # Test heartbeat message
        ws.send_text('{"type": "ping"}')
        reply = ws.receive_json()
        assert reply["event"] == "acknowledgment"
        assert reply["status"] == "received"


# 13. OpenAPI Documentation Availability
def test_openapi_schema(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    paths = openapi["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/grid" in paths
    assert "/api/v1/simulation/run" in paths
    assert "/api/v1/forecast" in paths
    assert "/api/v1/risk/analyze" in paths
    assert "/api/v1/optimization/run" in paths
    assert "/api/v1/scenarios/what-if" in paths
