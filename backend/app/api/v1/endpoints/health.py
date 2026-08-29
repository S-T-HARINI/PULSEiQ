from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the operational health status and metadata of the PULSEiQ API.",
)
async def get_health() -> HealthResponse:
    """Basic health check endpoint confirming the API service is up and running."""
    return HealthResponse(
        status="ok",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )
