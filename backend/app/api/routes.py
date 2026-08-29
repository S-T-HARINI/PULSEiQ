import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status

from backend.app.schemas.health import HealthResponse
from backend.app.schemas.grid import GridResponse
from backend.app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
)
from backend.app.schemas.forecast import (
    ForecastRequest,
    ForecastResponse,
    ForecastType,
)
from backend.app.schemas.risk import (
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
from backend.app.schemas.pipeline import (
    PipelineRunRequest,
    PipelineRunResponse,
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
from backend.app.services.pipeline_service import pipeline_service
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
@router.get(
    "/forecast",
    response_model=ForecastResponse,
    summary="Get Demand & Renewable Forecast",
    tags=["Forecast"],
    description="Retrieves time-series predictions for load demand, solar generation, or wind production using Person 3 AI models with analytical fallbacks.",
)
async def get_forecast(
    forecast_type: ForecastType = Query(ForecastType.LOAD, description="Target forecast type: load, solar, wind"),
    horizon_hours: int = Query(24, ge=1, le=168, description="Forecast horizon in hours (1-168)"),
) -> ForecastResponse:
    """Generates hourly forecasted values and confidence intervals across the specified horizon."""
    try:
        req = ForecastRequest(forecast_type=forecast_type, horizon_hours=horizon_hours)
        return forecast_service.generate_forecast(req)
    except Exception as e:
        logger.error(f"Forecast error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecasting calculation failed: {str(e)}",
        )


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
@router.get(
    "/simulation",
    response_model=SimulationRunResponse,
    summary="Get Grid Simulation Baseline",
    tags=["Simulation"],
    description="Executes a baseline grid state power-flow simulation calculating generation, demand, line loading, voltage/frequency indicators.",
)
async def get_simulation(
    load_growth_factor: Optional[float] = Query(1.0, ge=0.1, le=3.0, description="Load growth scaling multiplier"),
    contingency_event: Optional[str] = Query(None, description="Optional forced contingency asset ID"),
) -> SimulationRunResponse:
    """Runs a baseline grid power-flow simulation."""
    if contingency_event and not grid_service.component_exists(contingency_event):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contingency component '{contingency_event}' not found in grid topology.",
        )
    try:
        req = SimulationRunRequest(load_growth_factor=load_growth_factor, contingency_event=contingency_event)
        return simulation_service.run_simulation(req)
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation processing failed: {str(e)}",
        )


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
@router.get(
    "/risk",
    response_model=RiskAnalysisResponse,
    summary="Get Grid Risk Analysis",
    tags=["Risk"],
    description="Performs risk evaluation, identifying vulnerable components, critical load impacts, N-1 screening, and cascading failure indicators.",
)
async def get_risk(
    contingency_type: Optional[str] = Query("N-1", description="Contingency category: N-1, extreme_weather, etc."),
    failed_component_id: Optional[str] = Query(None, description="Forced component outage identifier"),
) -> RiskAnalysisResponse:
    """Evaluates grid contingency and probabilistic risk metrics."""
    if failed_component_id and not grid_service.component_exists(failed_component_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{failed_component_id}' not found in grid topology.",
        )
    try:
        req = RiskAnalysisRequest(contingency_type=contingency_type, failed_component_id=failed_component_id)
        return risk_service.analyze_risk(req)
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk analysis computation failed: {str(e)}",
        )


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
@router.get(
    "/optimization",
    response_model=OptimizationRunResponse,
    summary="Get Optimal Power Dispatch",
    tags=["Optimization"],
    description="Calculates optimal power generation dispatch, battery scheduling, backup generation, and recommended actions.",
)
async def get_optimization(
    objective: OptimizationObjective = Query(OptimizationObjective.COST_MINIMIZATION, description="Target optimization objective"),
    demand_mw: Optional[float] = Query(None, description="Optional target demand override in MW"),
) -> OptimizationRunResponse:
    """Calculates optimal unit commitment and dispatch schedule."""
    try:
        req = OptimizationRunRequest(objective=objective, demand_mw=demand_mw)
        return optimization_service.run_optimization(req)
    except Exception as e:
        logger.error(f"Optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization solver execution failed: {str(e)}",
        )


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
@router.get(
    "/scenario/what-if",
    response_model=ScenarioWhatIfResponse,
    summary="Get What-If Scenario Analysis",
    tags=["Scenarios"],
    description="Simulates default what-if scenarios (extreme_heatwave, solar_ramp_down, n1_line_trip, wind_storm_cutoff).",
)
@router.get(
    "/scenarios/what-if",
    response_model=ScenarioWhatIfResponse,
    include_in_schema=False,
)
@router.get(
    "/scenario",
    response_model=ScenarioWhatIfResponse,
    include_in_schema=False,
)
async def get_what_if_scenario(
    scenario_type: ScenarioType = Query(ScenarioType.EXTREME_HEATWAVE, description="Scenario type to simulate"),
    failed_component_id: Optional[str] = Query(None, description="Forced component outage ID"),
) -> ScenarioWhatIfResponse:
    """Evaluates the projected impact of a what-if scenario on grid generation, demand, and risk."""
    if failed_component_id and not grid_service.component_exists(failed_component_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{failed_component_id}' not found in grid topology.",
        )
    try:
        req = ScenarioWhatIfRequest(scenario_type=scenario_type, failed_component_id=failed_component_id)
        return scenario_service.evaluate_what_if(req)
    except Exception as e:
        logger.error(f"Scenario error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario evaluation failed: {str(e)}",
        )


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
# 8. Unified AI Intelligence Pipeline Endpoint
# ==========================================
@router.post(
    "/pipeline/run",
    response_model=PipelineRunResponse,
    summary="Run End-to-End AI/ML Intelligence Pipeline",
    tags=["Pipeline"],
    description="Coordinates end-to-end unified AI/ML execution across Forecasting, Physical Simulation, Graph Topology Analysis, Multi-Factor Risk Assessment, and Optimal Dispatch Optimization.",
)
@router.post(
    "/pipeline",
    response_model=PipelineRunResponse,
    include_in_schema=False,
)
async def run_ai_pipeline_endpoint(payload: Optional[PipelineRunRequest] = None) -> PipelineRunResponse:
    """Executes the complete unified AI/ML pipeline for the electricity grid."""
    req = payload or PipelineRunRequest()
    if req.contingency_event and not grid_service.component_exists(req.contingency_event):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid component '{req.contingency_event}' not found in grid topology.",
        )
    try:
        return pipeline_service.run_pipeline(req)
    except Exception as e:
        logger.error(f"Unified pipeline execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unified pipeline execution failed: {str(e)}",
        )


@router.get(
    "/pipeline/run",
    response_model=PipelineRunResponse,
    summary="Get End-to-End AI/ML Pipeline Snapshot",
    tags=["Pipeline"],
    description="Executes default unified AI/ML pipeline snapshot.",
)
@router.get(
    "/pipeline",
    response_model=PipelineRunResponse,
    include_in_schema=False,
)
async def get_ai_pipeline_endpoint(
    horizon_hours: int = Query(24, ge=1, le=168, description="Forecast horizon in hours"),
    include_simulation: bool = Query(True, description="Include DC power flow simulation"),
    include_optimization: bool = Query(True, description="Include dispatch optimization"),
) -> PipelineRunResponse:
    """Executes default unified AI/ML pipeline snapshot."""
    req = PipelineRunRequest(
        horizon_hours=horizon_hours,
        include_simulation=include_simulation,
        include_optimization=include_optimization,
    )
    try:
        return pipeline_service.run_pipeline(req)
    except Exception as e:
        logger.error(f"Unified pipeline execution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unified pipeline execution failed: {str(e)}",
        )


# ==========================================
# 9. Real-Time WebSocket Streaming Handlers
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
