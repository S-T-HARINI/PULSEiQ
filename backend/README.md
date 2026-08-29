 PULSEiQ — FastAPI Backend Service (Step 5: Real-Time Telemetry & WebSockets)

Welcome to the backend service for **PULSEiQ**, an AI-powered electricity grid simulation, risk analysis, and optimization platform.

---

## Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py                 # Exported router index
│   │   └── routes.py                   # REST & WebSocket API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── ai_bridge.py                # AI/ML module detection, dynamic binding & fallback bridge
│   │   └── config.py                   # Pydantic Settings & environment variables (TELEMETRY_INTERVAL_SECONDS)
│   ├── schemas/
│   │   ├── __init__.py                 # Pydantic schema export index
│   │   ├── forecast.py                 # ForecastRequest, ForecastResponse, ForecastDataPoint, ForecastType
│   │   ├── grid.py                     # GridNode, GridEdge, GridSummary, GridResponse
│   │   ├── health.py                   # HealthResponse schema with AI subsystem status
│   │   ├── optimization.py             # OptimizationRunRequest, OptimizationRunResponse, GeneratorDispatch
│   │   ├── risk.py                     # RiskAnalysisRequest, RiskAnalysisResponse, CriticalLoadImpact, AffectedComponent
│   │   ├── scenario.py                 # ScenarioWhatIfRequest, ScenarioWhatIfResponse, ScenarioType
│   │   ├── simulation.py               # SimulationRunRequest, SimulationRunResponse
│   │   └── telemetry.py                # GridTelemetryMessage, GridOperationalStatus, ClientControlMessage
│   ├── services/
│   │   ├── __init__.py                 # Services export index
│   │   ├── connection_manager.py       # Client WebSocket registry, connection, and broadcasting manager
│   │   ├── forecast_service.py         # Time-series forecasting service with AI module & fallback
│   │   ├── grid_service.py             # Digital Twin grid topology & telemetry service
│   │   ├── optimization_service.py     # Economic dispatch & unit commitment optimization service
│   │   ├── risk_service.py             # Contingency & Monte Carlo risk assessment service
│   │   ├── scenario_service.py         # What-if scenario simulation & impact evaluation service
│   │   ├── simulation_service.py       # Power-flow & grid state simulation service
│   │   └── telemetry_service.py        # Real-time telemetry generator and async broadcast loop
│   ├── __init__.py
│   └── main.py                         # FastAPI application entry point, root WebSocket endpoint & lifespan manager
├── tests/
│   ├── __init__.py
│   └── test_api.py                     # Automated 23-case pytest integration, contract & WebSocket test suite
├── .env.example                        # Environment variables template
├── requirements.txt                    # Dependencies (FastAPI, Uvicorn, Pydantic, SQLAlchemy, asyncpg, websockets, pytest, httpx)
└── README.md                           # Documentation
```

---

##  Getting Started

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- `pip` package manager

### 2. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp backend/.env.example backend/.env
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Run the Development Server
From the root repository directory:
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

---

##  Real-Time WebSocket Telemetry (`/ws/grid`)

The frontend live dashboard connects directly to:
```
ws://localhost:8000/ws/grid
```

### Connection & Lifecycle:
1. **Connect**: Accepts connection and registers client in `ConnectionManager`.
2. **Initial Snapshot**: Immediately emits the initial structured grid snapshot frame.
3. **Continuous Streaming**: Emits periodic telemetry updates every `TELEMETRY_INTERVAL_SECONDS` (default: `2.0s`).
4. **Clean Disconnect**: Handles `WebSocketDisconnect` cleanly, removing the client and releasing resources.

### Telemetry Message Schema (`GridTelemetryMessage`):
```json
{
  "message_type": "grid_telemetry",
  "timestamp": "2026-08-29T11:27:10.000Z",
  "grid_status": "NORMAL",
  "total_generation": 475.94,
  "total_demand": 462.04,
  "renewable_generation_percent": 49.47,
  "battery_soc": 78.50,
  "grid_risk_index": 0.14,
  "frequency_hz": 50.021,
  "line_utilization_avg": 56.4,
  "affected_components": [],
  "details": {
    "solar_generation_mw": 140.0,
    "wind_generation_mw": 95.0,
    "net_imbalance_mw": 13.9,
    "active_connections": 1
  }
}
```

---

##  REST API Endpoints

| Method | Endpoint | Description | Response Schema |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health and connected AI module status | [`HealthResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/health.py) |
| `GET` | `/api/v1/grid` | Digital Twin grid topology (nodes, transmission lines, summary metrics) | [`GridResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/grid.py) |
| `POST` | `/api/v1/forecast` | Time-series forecasting for Load, Solar, and Wind with P10/P90 confidence bands | [`ForecastResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/forecast.py) |
| `POST` | `/api/v1/simulation` | Execute power-flow and state simulation with per-line thermal loading | [`SimulationRunResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/simulation.py) |
| `POST` | `/api/v1/risk` | Contingency (N-1), critical hospital threat assessment, and cascading failure indicators | [`RiskAnalysisResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/risk.py) |
| `POST` | `/api/v1/optimization` | Optimal power dispatch, battery scheduling, backup generation, and recommended actions | [`OptimizationRunResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/optimization.py) |
| `POST` | `/api/v1/scenario/what-if` | What-if scenarios (Heatwave, Solar Ramp-Down, Wind Storm Cut-Off, N-1 Line Trip) | [`ScenarioWhatIfResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/scenario.py) |
| `WS` | `/ws/grid` | Real-time WebSocket streaming for grid telemetry & events | [`GridTelemetryMessage`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/telemetry.py) |

---

##  Running the Test Suite

Run all automated unit, integration, and WebSocket tests with pytest:
```bash
pytest backend/tests/ -v
```

---

##  Interactive Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
