from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    grid,
    simulation,
    forecast,
    risk,
    optimization,
    scenario,
    websockets,
)

api_router = APIRouter()

# Health check endpoint (GET /api/v1/health)
api_router.include_router(health.router, tags=["Health"])

# Grid state endpoint (GET /api/v1/grid)
api_router.include_router(grid.router, tags=["Grid"])

# Simulation endpoint (POST /api/v1/simulation)
api_router.include_router(simulation.router, tags=["Simulation"])

# Forecast endpoint (POST /api/v1/forecast)
api_router.include_router(forecast.router, tags=["Forecast"])

# Risk analysis endpoint (POST /api/v1/risk)
api_router.include_router(risk.router, tags=["Risk Analysis"])

# Optimization endpoint (POST /api/v1/optimization)
api_router.include_router(optimization.router, tags=["Optimization"])

# Scenario endpoint (POST /api/v1/scenario)
api_router.include_router(scenario.router, tags=["Scenarios"])

# WebSocket streaming endpoint (/api/v1/ws/live)
api_router.include_router(websockets.router, tags=["WebSockets"])
