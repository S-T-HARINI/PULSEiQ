import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.grid import (
    GridResponse,
    NodeType,
    NodeStatus,
    NodeCriticality,
)
from backend.app.schemas.telemetry import (
    GridTelemetryMessage,
    GridOperationalStatus,
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
from backend.app.services.connection_manager import ws_connection_manager
from backend.app.services.telemetry_service import telemetry_service
from backend.app.core.ai_bridge import ai_bridge


@pytest.fixture
def client():
    return TestClient(app)


# 1. Health Endpoint Test
def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "PULSEiQ" in data["service"]
    assert "ai_modules" in data
    assert "forecasting" in data["ai_modules"]


# 2. Root Endpoint Test
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert data["health_check"] == "/api/v1/health"
    assert data["grid_state"] == "/api/v1/grid"
    assert data["websocket_grid"] == "/ws/grid"


# 3. GET /api/v1/grid Data & Schema Validation Test
def test_get_grid_endpoint(client):
    response = client.get("/api/v1/grid")
    assert response.status_code == 200
    data = response.json()

    grid_model = GridResponse(**data)
    assert len(grid_model.nodes) == 50
    assert len(grid_model.edges) >= 40

    node_types = {n.type for n in grid_model.nodes}
    assert NodeType.CONVENTIONAL_GENERATOR in node_types
    assert NodeType.SOLAR_PLANT in node_types
    assert NodeType.WIND_PLANT in node_types
    assert NodeType.BATTERY in node_types
    assert NodeType.SUBSTATION in node_types
    assert NodeType.LOAD in node_types
    assert NodeType.CRITICAL_LOAD in node_types

    hospital = next((n for n in grid_model.nodes if n.type == NodeType.CRITICAL_LOAD), None)
    assert hospital is not None
    assert hospital.criticality == NodeCriticality.CRITICAL
    assert hospital.current_output_mw == 45.0

    summary = grid_model.summary
    assert summary.total_generation_mw > 0
    assert summary.total_demand_mw > 0
    assert summary.renewable_percentage > 0
    assert summary.battery_soc == 78.5
    assert 0.0 <= summary.grid_risk_index <= 1.0


# 4. Forecast Endpoint Tests (POST /api/v1/forecast)
@pytest.mark.parametrize("forecast_type", [
    ForecastType.LOAD,
    ForecastType.SOLAR,
    ForecastType.WIND,
])
def test_forecast_endpoint(client, forecast_type):
    payload = {
        "forecast_type": forecast_type.value,
        "horizon_hours": 24,
        "historical_demand_mw": [420.0, 430.0, 445.0, 460.0],
        "weather_info": {"temperature_c": 29.5, "solar_irradiance": 820.0},
    }
    response = client.post("/api/v1/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()

    fc_resp = ForecastResponse(**data)
    assert fc_resp.forecast_type == forecast_type
    assert fc_resp.horizon_hours == 24
    assert len(fc_resp.values) == 24
    assert fc_resp.peak_mw >= fc_resp.min_mw
    assert fc_resp.confidence_score > 0.0
    assert fc_resp.model_source in ["ai_module", "service_fallback"]


# 5. Simulation Endpoint Tests (POST /api/v1/simulation)
def test_simulation_endpoint(client):
    payload = {
        "scenario_id": "test_sim_01",
        "duration_hours": 24,
        "time_step_minutes": 60,
        "load_growth_factor": 1.12,
        "contingency_event": "line-north-central-1",
    }
    response = client.post("/api/v1/simulation", json=payload)
    assert response.status_code == 200
    data = response.json()

    sim_resp = SimulationRunResponse(**data)
    assert sim_resp.simulation_status == "completed"
    assert sim_resp.total_generation_mw > 0
    assert sim_resp.total_demand_mw > 0
    assert sim_resp.renewable_generation_mw > 0
    assert len(sim_resp.line_loading) > 0
    assert (48.0 <= sim_resp.frequency_hz <= 52.0) or (58.0 <= sim_resp.frequency_hz <= 62.0)
    assert "min_voltage_pu" in sim_resp.voltage_indicators
    assert 0.0 <= sim_resp.risk_index <= 1.0
    assert sim_resp.model_source in ["ai_module", "service_fallback"]


# 6. Risk Analysis Endpoint Test (POST /api/v1/risk)
def test_risk_analysis_endpoint(client):
    payload = {
        "contingency_type": "N-1",
        "failed_component_id": "line-north-central-1",
        "monte_carlo_iterations": 1000,
    }
    response = client.post("/api/v1/risk", json=payload)
    assert response.status_code == 200
    data = response.json()

    risk_resp = RiskAnalysisResponse(**data)
    assert risk_resp.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert len(risk_resp.vulnerable_components) > 0
    assert "overload_propagation_probability" in risk_resp.cascading_failure_indicators
    assert "n1_compliance_status" in risk_resp.n1_analysis
    assert risk_resp.model_source in ["ai_module", "service_fallback"]


# 7. Risk Analysis for Critical Hospital Outage
def test_risk_analysis_hospital_threat(client):
    payload = {
        "contingency_type": "N-1",
        "failed_component_id": "line-south-to-hospital",
    }
    response = client.post("/api/v1/risk", json=payload)
    assert response.status_code == 200
    data = response.json()

    risk_resp = RiskAnalysisResponse(**data)
    assert risk_resp.critical_load_impact.critical_load_at_risk is True
    assert risk_resp.critical_load_impact.critical_load_at_risk_mw >= 45.0
    assert any("Metro University Hospital" in fac for fac in risk_resp.critical_load_impact.affected_critical_facilities)
    assert risk_resp.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]


# 8. Optimization Endpoint Test (POST /api/v1/optimization)
@pytest.mark.parametrize("objective", [
    OptimizationObjective.COST_MINIMIZATION,
    OptimizationObjective.EMISSION_REDUCTION,
    OptimizationObjective.RELIABILITY_MAXIMIZATION,
])
def test_optimization_endpoint(client, objective):
    payload = {
        "objective": objective.value,
        "demand_mw": 460.0,
        "battery_availability": {"soc_percent": 78.5, "capacity_mw": 80.0},
    }
    response = client.post("/api/v1/optimization", json=payload)
    assert response.status_code == 200
    data = response.json()

    opt_resp = OptimizationRunResponse(**data)
    assert opt_resp.optimization_status == "optimal"
    assert opt_resp.objective == objective
    assert len(opt_resp.generator_dispatch) >= 3
    assert len(opt_resp.recommended_actions) > 0
    assert opt_resp.cost_estimate_usd > 0
    assert opt_resp.model_source in ["ai_module", "service_fallback"]


# 9. What-If Scenario Endpoint Tests (POST /api/v1/scenario/what-if)
@pytest.mark.parametrize("scenario_type", [
    ScenarioType.EXTREME_HEATWAVE,
    ScenarioType.SOLAR_RAMP_DOWN,
    ScenarioType.N1_LINE_TRIP,
    ScenarioType.WIND_STORM_CUTOFF,
])
def test_what_if_scenario_endpoint(client, scenario_type):
    payload = {
        "scenario_type": scenario_type.value,
        "name": f"Test {scenario_type.value}",
        "demand_multiplier": 1.25,
        "battery_available": True,
    }
    response = client.post("/api/v1/scenario/what-if", json=payload)
    assert response.status_code == 200
    data = response.json()

    scen_resp = ScenarioWhatIfResponse(**data)
    assert scen_resp.scenario_type == scenario_type
    assert scen_resp.changed_demand_mw > 0
    assert scen_resp.changed_generation_mw > 0
    assert 0.0 <= scen_resp.resulting_risk_index <= 1.0
    assert len(scen_resp.recommended_response) > 0
    assert scen_resp.model_source in ["ai_module", "service_fallback"]


# 10. Invalid Scenario Type Handled (422)
def test_invalid_scenario_type_rejected(client):
    payload = {"scenario_type": "alien_invasion_surge"}
    response = client.post("/api/v1/scenario/what-if", json=payload)
    assert response.status_code == 422
    assert response.json()["error"] == "Unprocessable Entity"


# 11. Invalid Component ID Handled (404)
def test_invalid_component_id_rejected(client):
    payload = {
        "scenario_type": "n1_line_trip",
        "failed_component_id": "nonexistent_line_999",
    }
    response = client.post("/api/v1/scenario/what-if", json=payload)
    assert response.status_code == 404
    assert "not found in grid topology" in response.json()["detail"]


# 12. Root-Level WebSocket Test (/ws/grid)
def test_root_websocket_grid_stream(client):
    with client.websocket_connect("/ws/grid") as ws:
        # Initial snapshot validation
        frame = ws.receive_json()
        telemetry = GridTelemetryMessage(**frame)
        assert telemetry.message_type == "grid_telemetry"
        assert telemetry.grid_status in [
            GridOperationalStatus.NORMAL,
            GridOperationalStatus.WARNING,
            GridOperationalStatus.ALERT,
            GridOperationalStatus.CRITICAL,
        ]
        assert telemetry.total_generation > 0
        assert telemetry.total_demand > 0
        assert 0.0 <= telemetry.renewable_generation_percent <= 100.0
        assert 0.0 <= telemetry.battery_soc <= 100.0
        assert 0.0 <= telemetry.grid_risk_index <= 1.0
        assert 48.0 <= telemetry.frequency_hz <= 52.0

        # Heartbeat bidirectional exchange
        ws.send_text('{"action": "ping", "client_id": "test_client"}')
        reply = ws.receive_json()
        assert reply["event"] == "acknowledgment"
        assert reply["status"] == "received"
        assert reply["payload"]["action"] == "ping"


# 13. API v1 WebSocket Test (/api/v1/ws/grid)
def test_apiv1_websocket_grid_stream(client):
    with client.websocket_connect("/api/v1/ws/grid") as ws:
        frame = ws.receive_json()
        telemetry = GridTelemetryMessage(**frame)
        assert telemetry.message_type == "grid_telemetry"
        assert telemetry.total_generation > 0


# 14. Telemetry Service Generator & Scenario State Override Test
def test_telemetry_service_generation_and_override():
    initial = telemetry_service.generate_current_telemetry()
    assert isinstance(initial, GridTelemetryMessage)
    assert initial.grid_status == GridOperationalStatus.NORMAL

    # Simulate scenario impact override
    telemetry_service.set_scenario_impact(
        risk_index=0.82,
        status=GridOperationalStatus.CRITICAL,
        affected_components=["line-south-to-hospital", "load-hospital-metro"],
    )
    overridden = telemetry_service.generate_current_telemetry()
    assert overridden.grid_risk_index == 0.82
    assert overridden.grid_status == GridOperationalStatus.CRITICAL
    assert "line-south-to-hospital" in overridden.affected_components

    # Reset
    telemetry_service.reset_scenario_impact()
    reset = telemetry_service.generate_current_telemetry()
    assert reset.grid_status == GridOperationalStatus.NORMAL


# 15. OpenAPI Documentation Availability Test
def test_openapi_schema(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    paths = openapi["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/grid" in paths
    assert "/api/v1/forecast" in paths
    assert "/api/v1/simulation" in paths
    assert "/api/v1/risk" in paths
    assert "/api/v1/optimization" in paths
    assert "/api/v1/scenario/what-if" in paths


# 16. AI Bridge Resilience Test
def test_ai_bridge_resilience():
    status_summary = ai_bridge.get_status_summary()
    assert isinstance(status_summary, dict)
    assert "forecasting" in status_summary
    assert "simulation" in status_summary
    assert "risk_engine" in status_summary
    assert "optimization" in status_summary
