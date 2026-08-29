import uuid
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.scenario import ScenarioRequest, ScenarioResponse, ScenarioType
from backend.app.services.grid_service import grid_service

router = APIRouter()


@router.post(
    "/scenario",
    response_model=ScenarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Create & Configure What-If Scenario",
    description="Configures what-if grid conditions and assumptions (e.g., extreme heatwave, solar ramp-down, wind storm, N-1 line trip).",
)
async def create_scenario(payload: ScenarioRequest) -> ScenarioResponse:
    """Accepts a what-if scenario definition, validates grid asset identifiers,
    and returns structured scenario assumptions for downstream AI/ML and simulation engines.
    """
    # Validate failed component ID if specified
    if payload.failed_component_id:
        if not grid_service.component_exists(payload.failed_component_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grid component '{payload.failed_component_id}' not found in grid topology.",
            )

    scenario_id = f"scen_{uuid.uuid4().hex[:8]}"
    display_name = payload.name or f"{payload.scenario_type.value.replace('_', ' ').title()} Scenario"

    # Compile structured assumptions summary for future AI/simulation handoff
    assumptions_summary = {
        "scenario_type": payload.scenario_type.value,
        "demand_scaling": f"{payload.demand_multiplier * 100:.1f}% of baseline",
        "solar_scaling": f"{payload.solar_multiplier * 100:.1f}% of rated output",
        "wind_scaling": f"{payload.wind_multiplier * 100:.1f}% of rated output",
        "battery_dispatch_enabled": payload.battery_available,
        "forced_outages": [payload.failed_component_id] if payload.failed_component_id else [],
    }

    return ScenarioResponse(
        scenario_id=scenario_id,
        scenario_type=payload.scenario_type,
        name=display_name,
        status="configured",
        message=f"Scenario '{display_name}' ({payload.scenario_type.value}) configured successfully. Assumptions prepared for simulation engine.",
        applied_parameters={
            "demand_multiplier": payload.demand_multiplier,
            "solar_multiplier": payload.solar_multiplier,
            "wind_multiplier": payload.wind_multiplier,
            "battery_available": payload.battery_available,
            "failed_component_id": payload.failed_component_id,
        },
        assumptions_summary=assumptions_summary,
    )
