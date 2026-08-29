import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure repository root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.core.config import settings
from backend.app.api.routes import router as api_router, handle_telemetry_websocket
from backend.app.services.telemetry_service import telemetry_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager handling application startup and shutdown tasks."""
    telemetry_service.start_background_broadcaster()
    yield
    telemetry_service.stop_background_broadcaster()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom validation exception handler for clean JSON error reporting
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for err in exc.errors():
        location = " -> ".join(str(loc) for loc in err.get("loc", []))
        formatted_errors.append({
            "field": location,
            "message": err.get("msg"),
            "type": err.get("type"),
        })
    return JSONResponse(
        status_code=422,
        content={
            "error": "Unprocessable Entity",
            "message": "The request payload contains invalid fields or unsupported types.",
            "details": formatted_errors,
        },
    )


# Configure CORS for Next.js frontend (http://localhost:3000, http://127.0.0.1:3000)
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes with configured prefix
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root-level WebSocket endpoint (/ws/grid) as requested for frontend live dashboard
@app.websocket("/ws/grid")
async def root_websocket_grid_stream(websocket: WebSocket) -> None:
    """Root-level WebSocket endpoint streaming continuous real-time grid telemetry."""
    await handle_telemetry_websocket(websocket)


@app.websocket("/ws/telemetry")
async def root_websocket_telemetry_stream(websocket: WebSocket) -> None:
    """Root-level WebSocket telemetry stream alias."""
    await handle_telemetry_websocket(websocket)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing service metadata and navigation endpoints."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs_url": "/docs",
        "health_check": f"{settings.API_V1_PREFIX}/health",
        "grid_state": f"{settings.API_V1_PREFIX}/grid",
        "websocket_grid": "/ws/grid",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
