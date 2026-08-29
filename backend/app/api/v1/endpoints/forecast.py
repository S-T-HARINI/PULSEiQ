from fastapi import APIRouter
from backend.app.schemas.forecast import ForecastRequest, ForecastResponse

router = APIRouter()


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Generate AI/ML Forecast",
    description="Requests load, renewable generation, or price forecasts for the grid (Placeholder contract for future AI/ML forecasting model).",
)
async def generate_forecast(payload: ForecastRequest) -> ForecastResponse:
    """Forecasting contract endpoint. AI/ML forecasting models will be integrated in subsequent phases."""
    return ForecastResponse(
        status="not_implemented",
        message="AI/ML forecasting engine will be connected in a later step.",
        contract_info={
            "target": payload.target.value,
            "horizon_hours": payload.horizon_hours,
            "model_type": payload.model_type.value if payload.model_type else "ensemble",
            "region_id": payload.region_id,
        },
    )
