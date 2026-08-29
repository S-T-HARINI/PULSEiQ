import asyncio
import json
import logging
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
from backend.app.schemas.telemetry import (
    GridTelemetryMessage,
)

from backend.app.services.grid_service import grid_service
from backend.app.services.simulation_service import simulation_service
from backend.app.services.forecast_service import forecast_service
from backend.app.services.risk_service import risk_service
from backend.app.services.optimization_service import optimization_service
from backend.app.services.scenario_service import scenario_service
from backend.app.services.connection_manager import ws_connection_manager
from backend.app.services.telemetry_service import telemetry_service
from backend.app.core.ai_bridge import ai_bridge
from backend.app.core.config import settings

logger = logging.getLogger("pulseiq.api.routes")
router = APIRouter()


# ==========================================
# 1. Health & AI Status Endpoint
# ==========================================
@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health & System Status Check",
    tags=["Health"],
    description="Returns API status, version, and the operational connection status of AI/ML modules and fallback services.",
)
async def get_health() -> HealthResponse:
    """Operational health check endpoint confirming API availability and AI/ML bridge status."""
    return HealthResponse(
        status="healthy",
        service="PULSEiQ Backend",
        version="1.0.0",
        ai_modules=ai_bridge.get_status_summary(),
        environment=settings.ENVIRONMENT,
    )


# ==========================================
# 2. Grid Topology & Telemetry Endpoint
# ==========================================
@router.get(
    "/grid",
    response_model=GridResponse,
    summary="Get Grid Representation & Telemetry",
    tags=["Grid"],
    description="Retrieves current grid representation (generators, solar, wind, battery, substations, loads, critical hospital load, transmission lines, and summary metrics) for the frontend Grid Twin.",
)
async def get_grid_state() -> GridResponse:
    """Returns the complete digital twin state of the electricity grid."""
    return grid_service.get_grid_state()


# ==========================================
# 3. Time-Series Forecasting Endpoint
# ==========================================
@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate Demand & Renewable Forecast",
    tags=["Forecast"],
    description="Generates time-series predictions for load demand, solar generation, or wind production using Person 3 AI models with analytical fallbacks.",
)
async def generate_forecast(payload: ForecastRequest) -> ForecastResponse:
    """Generates hourly forecasted values and confidence intervals across the specified horizon."""
    try:
        return forecast_service.generate_forecast(payload)
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecasting calculation failed: {str(e)}",
        )


# ==========================================
# 4. Grid Simulation Endpoint
# ==========================================
@router.post(
    "/simulation",
    response_model=SimulationRunResponse,
    summary="Execute Grid Simulation",
    tags=["Simulation"],
    description="Executes a grid state power-flow simulation calculating generation, demand, line loading, voltage/frequency indicators, and affected components.",
)
@router.post(
    "/simulation/run",
    response_model=SimulationRunResponse,
    include_in_schema=False,
)
async def run_simulation(payload: SimulationRunRequest) -> SimulationRunResponse:
    """Runs an AC/DC grid state simulation via Person 3 simulation engine or physics-based service fallback."""
    if payload.contingency_event and not grid_service.component_exists(payload.contingency_event):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contingency component '{payload.contingency_event}' not found in grid topology.",
        )
    try:
        return simulation_service.run_simulation(payload)
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation processing failed: {str(e)}",
        )


# ==========================================
# 5. Risk Analysis Endpoint
# ==========================================
@router.post(
    "/risk",
    response_model=RiskAnalysisResponse,
    summary="Analyze Grid Risk & Contingencies",
    tags=["Risk"],
    description="Performs risk evaluation, identifying vulnerable components, critical load impacts, N-1 screening, and cascading failure indicators.",
)
@router.post(
    "/risk/analyze",
    response_model=RiskAnalysisResponse,
    include_in_schema=False,
)
async def analyze_risk(payload: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """Evaluates grid contingency and probabilistic risk metrics."""
    if payload.failed_component_id and not grid_service.component_exists(payload.failed_component_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{payload.failed_component_id}' not found in grid topology.",
        )
    try:
        return risk_service.analyze_risk(payload)
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk analysis computation failed: {str(e)}",
        )


# ==========================================
# 6. Optimization Endpoint
# ==========================================
@router.post(
    "/optimization",
    response_model=OptimizationRunResponse,
    summary="Solve Grid Optimization & Dispatch",
    tags=["Optimization"],
    description="Calculates optimal power generation dispatch, battery scheduling, backup generation, and recommended actions using Person 3 solvers or merit-order fallback.",
)
@router.post(
    "/optimization/run",
    response_model=OptimizationRunResponse,
    include_in_schema=False,
)
async def run_optimization(payload: OptimizationRunRequest) -> OptimizationRunResponse:
    """Calculates optimal unit commitment and dispatch schedule based on target objective."""
    try:
        return optimization_service.run_optimization(payload)
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization solver execution failed: {str(e)}",
        )


# ==========================================
# 7. What-If Scenario Endpoint
# ==========================================
@router.post(
    "/scenario/what-if",
    response_model=ScenarioWhatIfResponse,
    summary="Evaluate What-If Scenario",
    tags=["Scenarios"],
    description="Simulates what-if scenarios (extreme_heatwave, solar_ramp_down, n1_line_trip, wind_storm_cutoff) and returns changed demand/generation, resulting risk, critical-load impact, and recommended responses.",
)
@router.post(
    "/scenarios/what-if",
    response_model=ScenarioWhatIfResponse,
    include_in_schema=False,
)
@router.post(
    "/scenario",
    response_model=ScenarioWhatIfResponse,
    include_in_schema=False,
)
async def run_what_if_scenario(payload: ScenarioWhatIfRequest) -> ScenarioWhatIfResponse:
    """Evaluates the projected impact of a what-if scenario on grid generation, demand, and risk."""
    if payload.failed_component_id and not grid_service.component_exists(payload.failed_component_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{payload.failed_component_id}' not found in grid topology.",
        )
    try:
        return scenario_service.evaluate_what_if(payload)
    except Exception as e:
        logger.error(f"Scenario error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario evaluation failed: {str(e)}",
        )


# ==========================================
# 8. Real-Time WebSocket Streaming Handlers
# ==========================================
async def handle_telemetry_websocket(websocket: WebSocket) -> None:
    """Core WebSocket handler streaming continuous telemetry snapshots and handling heartbeats."""
    await ws_connection_manager.connect(websocket)

    # 1. Send immediate initial grid snapshot frame
    initial_snapshot = telemetry_service.generate_current_telemetry()
    await ws_connection_manager.send_message(websocket, initial_snapshot)

    # 2. Continuous telemetry streaming background task for this client
    async def stream_telemetry_loop():
        interval = max(0.5, settings.TELEMETRY_INTERVAL_SECONDS)
        while True:
            await asyncio.sleep(interval)
            update_frame = telemetry_service.generate_current_telemetry()
            await ws_connection_manager.send_message(websocket, update_frame)

    stream_task = asyncio.create_task(stream_telemetry_loop())

    # 3. Client receiver loop for bidirectional commands / heartbeats
    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                payload = json.loads(text_data)
            except Exception:
                payload = {"raw": text_data}

            await websocket.send_json({
                "event": "acknowledgment",
                "status": "received",
                "payload": payload,
            })
    except WebSocketDisconnect:
        logger.info("Client disconnected from telemetry stream.")
    except Exception as e:
        logger.debug(f"WebSocket session terminated: {e}")
    finally:
        stream_task.cancel()
        ws_connection_manager.disconnect(websocket)


@router.websocket("/ws/grid")
async def websocket_grid_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint streaming continuous grid telemetry frames."""
    await handle_telemetry_websocket(websocket)


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket) -> None:
    """Telemetry stream alias."""
    await handle_telemetry_websocket(websocket)


@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket) -> None:
    """Live stream alias."""
    await handle_telemetry_websocket(websocket)
