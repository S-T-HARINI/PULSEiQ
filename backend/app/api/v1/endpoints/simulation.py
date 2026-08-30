from fastapi import APIRouter
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse

router = APIRouter()


@router.post(
    "/simulation",
    response_model=SimulationResponse,
    summary="Trigger Grid Simulation",
    description="Initiates an electricity grid simulation run (Placeholder contract for future simulation engine).",
)
async def trigger_simulation(payload: SimulationRequest) -> SimulationResponse:
    """Simulation contract endpoint. Business logic and power-flow engines will be connected in subsequent phases."""
    return SimulationResponse(
        status="not_implemented",
        message="Simulation engine will be connected in a later step.",
        contract_info={
            "module": "simulation_engine",
            "received_scenario_id": payload.scenario_id,
            "duration_hours": payload.duration_hours,
            "time_step_minutes": payload.time_step_minutes,
        },
    )
