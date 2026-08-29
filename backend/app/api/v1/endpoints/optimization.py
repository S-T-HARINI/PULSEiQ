from fastapi import APIRouter
from backend.app.schemas.optimization import OptimizationRequest, OptimizationResponse

router = APIRouter()


@router.post(
    "/optimization",
    response_model=OptimizationResponse,
    summary="Run Grid Optimization Solver",
    description="Calculates optimal power generation dispatch, battery scheduling, or grid re-configuration (Placeholder contract for future mathematical optimization solver).",
)
async def run_optimization(payload: OptimizationRequest) -> OptimizationResponse:
    """Optimization solver contract endpoint. Mathematical solvers and OPF engines will be integrated in subsequent phases."""
    return OptimizationResponse(
        status="not_implemented",
        message="Grid optimization engine will be connected in a later step.",
        contract_info={
            "objective": payload.objective.value,
            "time_horizon_hours": payload.time_horizon_hours,
            "constraints_count": len(payload.constraints),
            "participating_assets": payload.participating_assets,
        },
    )
