from fastapi import APIRouter
from backend.app.schemas.grid import GridResponse
from backend.app.services.grid_service import grid_service

router = APIRouter()


@router.get(
    "/grid",
    response_model=GridResponse,
    summary="Get Grid Topology and Real-Time State",
    description="Retrieves the complete electricity grid topology (nodes, transmission edges, and summary metrics) compatible with the Grid Twin.",
)
async def get_grid_state() -> GridResponse:
    """Returns the current electricity grid topology and aggregate metrics."""
    return grid_service.get_grid_state()
