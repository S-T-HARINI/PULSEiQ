from typing import List
from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.grid import (
    CustomGridCreate,
    CustomGridSummary,
    CustomGridUpdate,
    GridActivationResponse,
    GridDetailResponse,
    GridResponse,
)
from backend.app.services.grid_service import grid_service

router = APIRouter()


@router.get(
    "/grid",
    response_model=GridResponse,
    summary="Get Active Grid Topology and Real-Time State",
    description="Retrieves the active electricity grid topology (nodes, transmission edges, and summary metrics) compatible with the SCADA Grid Twin.",
)
async def get_grid_state() -> GridResponse:
    """Returns the current active electricity grid topology and aggregate metrics."""
    return grid_service.get_grid_state()


@router.post(
    "/grid/custom",
    response_model=GridDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Custom Electricity Grid",
    description="Registers a user-defined custom grid in the in-memory registry after topological validation.",
)
async def create_custom_grid(grid_data: CustomGridCreate) -> GridDetailResponse:
    """Creates and validates a new custom electricity grid."""
    try:
        return grid_service.create_custom_grid(grid_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/grid/custom",
    response_model=List[CustomGridSummary],
    summary="List All Grids (Reference and Custom)",
    description="Returns summary metadata for all registered reference and custom digital twins.",
)
async def list_custom_grids() -> List[CustomGridSummary]:
    """Lists summaries of all registered reference and custom grids."""
    return grid_service.list_grids()


@router.get(
    "/grid/custom/{grid_id}",
    response_model=GridDetailResponse,
    summary="Get Custom or Reference Grid Detail by ID",
    description="Retrieves full topology and component properties for a specific grid by ID.",
)
async def get_custom_grid_by_id(grid_id: str) -> GridDetailResponse:
    """Retrieves detailed topology for a specific grid by ID."""
    detail = grid_service.get_grid_detail(grid_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grid with ID '{grid_id}' not found in registry.",
        )
    return detail


@router.put(
    "/grid/custom/{grid_id}",
    response_model=GridDetailResponse,
    summary="Update Custom Grid Topology",
    description="Modifies an existing custom grid's topology, component parameters, or metadata.",
)
async def update_custom_grid(grid_id: str, update_data: CustomGridUpdate) -> GridDetailResponse:
    """Updates an existing custom grid."""
    try:
        return grid_service.update_custom_grid(grid_id, update_data)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/grid/custom/{grid_id}",
    summary="Delete Custom Grid",
    description="Removes a custom grid from the in-memory registry.",
)
async def delete_custom_grid(grid_id: str):
    """Deletes a custom grid by ID."""
    try:
        deleted = grid_service.delete_custom_grid(grid_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Custom grid with ID '{grid_id}' not found.",
            )
        return {"status": "deleted", "grid_id": grid_id, "message": f"Custom grid '{grid_id}' successfully removed."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/grid/active/{grid_id}",
    response_model=GridActivationResponse,
    summary="Set Active Grid for SCADA & AI/ML Pipelines",
    description="Selects and activates a specific grid (reference or custom) across the platform.",
)
async def set_active_grid(grid_id: str) -> GridActivationResponse:
    """Activates a specific grid for platform operations."""
    try:
        return grid_service.set_active_grid(grid_id)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

