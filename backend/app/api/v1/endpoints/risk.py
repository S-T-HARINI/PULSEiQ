from fastapi import APIRouter
from backend.app.schemas.risk import RiskAnalysisRequest, RiskAnalysisResponse

router = APIRouter()


@router.post(
    "/risk",
    response_model=RiskAnalysisResponse,
    summary="Perform Monte Carlo Risk Analysis",
    description="Initiates contingency (N-1, extreme weather) and probabilistic risk calculations (Placeholder contract for future Monte Carlo / risk engine).",
)
async def perform_risk_analysis(payload: RiskAnalysisRequest) -> RiskAnalysisResponse:
    """Risk analysis contract endpoint. Monte Carlo and probabilistic risk engines will be connected in subsequent phases."""
    return RiskAnalysisResponse(
        status="not_implemented",
        message="Monte Carlo risk engine will be connected in a later step.",
        contract_info={
            "contingency_types": payload.contingency_types,
            "monte_carlo_iterations": payload.monte_carlo_iterations,
            "region_id": payload.region_id,
            "risk_threshold": payload.risk_threshold,
        },
    )
