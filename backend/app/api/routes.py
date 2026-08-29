import json
from typing import List
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from backend.app.schemas.health import HealthResponse
from backend.app.schemas.grid import GridResponse
from backend.app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
)
from backend.app.schemas.forecast import (
    ForecastRequest,
    ForecastResponse,
)
from backend.app.schemas.risk import (
    RiskAnalysisRequest,
    RiskAnalysisResponse,
)
from backend.app.schemas.optimization import (
    OptimizationRunRequest,
    OptimizationRunResponse,
)
from backend.app.schemas.scenario import (
    ScenarioWhatIfRequest,
    ScenarioWhatIfResponse,
)

from backend.app.services.grid_service import grid_service
from backend.app.services.simulation_service import simulation_service
from backend.app.services.forecast_service import forecast_service
from backend.app.services.risk_service import risk_service
from backend.app.services.optimization_service import optimization_service
from backend.app.services.scenario_service import scenario_service

router = APIRouter()


# ==========================================
# 1. Health Endpoint
# ==========================================
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["Health"],
    description="Returns backend service health status, app name, version, and execution timestamp.",
)
async def get_health() -> HealthResponse:
    """Operational health check endpoint for frontend and monitoring services."""
    return HealthResponse(
        status="healthy",
        service="PULSEiQ Backend",
        version="1.0.0",
        environment="development",
    )


# ==========================================
# 2. Grid Topology & State Endpoint
# ==========================================
@router.get(
    "/grid",
    response_model=GridResponse,
    summary="Get Grid Topology & Telemetry",
    tags=["Grid"],
    description="Retrieves current grid topology, generators, substations, loads, transmission lines, and summary metrics.",
)
async def get_grid_state() -> GridResponse:
    """Returns the complete digital twin state of the electricity grid."""
    return grid_service.get_grid_state()


# ==========================================
# 3. Simulation Endpoint
# ==========================================
@router.post(
    "/simulation/run",
    response_model=SimulationRunResponse,
    summary="Run Grid Simulation",
    tags=["Simulation"],
    description="Executes a grid state simulation calculating power balance, line loadings, frequency, voltages, and risk.",
)
@router.post(
    "/simulation",
    response_model=SimulationRunResponse,
    include_in_schema=False,
)
async def run_simulation(payload: SimulationRunRequest) -> SimulationRunResponse:
    """Runs a grid power-flow simulation based on input parameters and contingencies."""
    if payload.contingency_event and not grid_service.component_exists(payload.contingency_event):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contingency component '{payload.contingency_event}' not found in grid topology.",
        )
    return simulation_service.run_simulation(payload)


# ==========================================
# 4. Forecast Endpoint
# ==========================================
@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate Forecast",
    tags=["Forecast"],
    description="Generates hourly time-series predictions for load demand, solar generation, or wind production.",
)
async def generate_forecast(payload: ForecastRequest) -> ForecastResponse:
    """Generates time-series forecast data over the requested horizon."""
    return forecast_service.generate_forecast(payload)


# ==========================================
# 5. Risk Analysis Endpoint
# ==========================================
@router.post(
    "/risk/analyze",
    response_model=RiskAnalysisResponse,
    summary="Analyze Grid Risk",
    tags=["Risk"],
    description="Analyzes grid operational risks, N-1 contingencies, affected components, and cascading failure probabilities.",
)
@router.post(
    "/risk",
    response_model=RiskAnalysisResponse,
    include_in_schema=False,
)
async def analyze_risk(payload: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """Performs risk evaluation for specified contingency conditions."""
    if payload.failed_component_id and not grid_service.component_exists(payload.failed_component_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{payload.failed_component_id}' not found in grid topology.",
        )
    return risk_service.analyze_risk(payload)


# ==========================================
# 6. Optimization Endpoint
# ==========================================
@router.post(
    "/optimization/run",
    response_model=OptimizationRunResponse,
    summary="Run Grid Optimization",
    tags=["Optimization"],
    description="Calculates optimal power generation dispatch, battery scheduling, and operating costs.",
)
@router.post(
    "/optimization",
    response_model=OptimizationRunResponse,
    include_in_schema=False,
)
async def run_optimization(payload: OptimizationRunRequest) -> OptimizationRunResponse:
    """Calculates optimal unit commitment and dispatch schedule based on objective."""
    return optimization_service.run_optimization(payload)


# ==========================================
# 7. What-If Scenario Endpoint
# ==========================================
@router.post(
    "/scenarios/what-if",
    response_model=ScenarioWhatIfResponse,
    summary="Run What-If Scenario",
    tags=["Scenarios"],
    description="Simulates what-if grid conditions: extreme heatwave, solar ramp-down, N-1 line trip, or wind storm.",
)
@router.post(
    "/scenario",
    response_model=ScenarioWhatIfResponse,
    include_in_schema=False,
)
async def run_what_if_scenario(payload: ScenarioWhatIfRequest) -> ScenarioWhatIfResponse:
    """Evaluates the projected impact of a what-if scenario on generation, demand, and risk."""
    if payload.failed_component_id and not grid_service.component_exists(payload.failed_component_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{payload.failed_component_id}' not found in grid topology.",
        )
    return scenario_service.evaluate_what_if(payload)


# ==========================================
# 8. WebSocket Telemetry Streaming
# ==========================================
class TelemetryConnectionManager:
    """Manages active WebSocket client connections for real-time grid telemetry broadcasting."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict) -> None:
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


ws_manager = TelemetryConnectionManager()


@router.websocket("/ws/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket) -> None:
    """Real-time WebSocket endpoint streaming structured grid telemetry and system status."""
    await ws_manager.connect(websocket)
    grid_state = grid_service.get_grid_state()
    try:
        # Initial telemetry snapshot frame
        await websocket.send_json({
            "timestamp": grid_state.timestamp,
            "frequency": 50.02,
            "total_generation_mw": grid_state.summary.total_generation_mw,
            "total_demand_mw": grid_state.summary.total_demand_mw,
            "risk_index": grid_state.summary.grid_risk_index,
            "renewable_percentage": grid_state.summary.renewable_percentage,
            "battery_soc": grid_state.summary.battery_soc,
            "status": "connected",
        })
        while True:
            text_data = await websocket.receive_text()
            try:
                payload = json.loads(text_data)
            except Exception:
                payload = {"raw": text_data}

            # Response acknowledgment frame
            await websocket.send_json({
                "event": "acknowledgment",
                "status": "received",
                "payload": payload,
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# Aliases for backward compatibility with Step 2 clients
@router.websocket("/ws/grid")
async def websocket_grid_alias(websocket: WebSocket) -> None:
    await websocket_telemetry_stream(websocket)


@router.websocket("/ws/live")
async def websocket_live_alias(websocket: WebSocket) -> None:
    await websocket_telemetry_stream(websocket)
