# PULSEiQ — FastAPI Backend Service (Step 3)

Welcome to the backend service for **PULSEiQ**, an AI-powered electricity grid simulation, risk analysis, and optimization platform.

---

## 📁 Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                 # Unified REST & WebSocket API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                 # Pydantic Settings & environment variables
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── forecast.py               # Forecast request/response models & ForecastType enum
│   │   ├── grid.py                   # Grid topology, nodes, edges & summary models
│   │   ├── health.py                 # Health check response model
│   │   ├── optimization.py           # Optimization request/response models & dispatch
│   │   ├── risk.py                   # Risk analysis request/response models & RiskLevel
│   │   ├── scenario.py               # What-if scenario models & ScenarioType enum
│   │   └── simulation.py             # Simulation run request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── forecast_service.py       # Time-series forecasting service (Load, Solar, Wind)
│   │   ├── grid_service.py           # Grid data layer service (topology & telemetry)
│   │   ├── optimization_service.py   # Economic dispatch & unit commitment optimization
│   │   ├── risk_service.py           # Contingency & Monte Carlo risk assessment service
│   │   ├── scenario_service.py       # What-if operational scenario simulation service
│   │   └── simulation_service.py     # Power-flow & grid state simulation service
│   ├── __init__.py
│   └── main.py                       # FastAPI application entry point & CORS configuration
├── tests/
│   ├── __init__.py
│   └── test_api.py                   # Automated 20-case pytest integration test suite
├── .env.example                      # Sample environment variables
├── requirements.txt                  # Python dependencies
└── README.md                         # Documentation
```

---

## 🚀 Getting Started

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

## 📡 API Endpoints (Step 3)

| Method | Endpoint | Description | Response Schema |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Operational health check | [`HealthResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/health.py) |
| `GET` | `/api/v1/grid` | Digital Twin grid topology (nodes, edges, summary metrics) | [`GridResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/grid.py) |
| `POST` | `/api/v1/simulation/run` | Execute power-flow & state simulation | [`SimulationRunResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/simulation.py) |
| `POST` | `/api/v1/forecast` | Time-series forecasting for Load, Solar, and Wind | [`ForecastResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/forecast.py) |
| `POST` | `/api/v1/risk/analyze` | Contingency (N-1) and probabilistic risk analysis | [`RiskAnalysisResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/risk.py) |
| `POST` | `/api/v1/optimization/run` | Optimal power dispatch, battery scheduling & cost estimation | [`OptimizationRunResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/optimization.py) |
| `POST` | `/api/v1/scenarios/what-if` | What-if scenarios (Heatwave, Solar Ramp-Down, Wind Storm, N-1) | [`ScenarioWhatIfResponse`](file:///c:/Users/chandini/PULSEiQ/backend/app/schemas/scenario.py) |
| `WS` | `/api/v1/ws/telemetry` | Real-time WebSocket streaming for grid telemetry & events | Telemetry JSON Frames |

---

## 🧪 Running the Test Suite

Run all automated unit and integration tests with pytest:
```bash
pytest backend/tests/ -v
```

---

## 📖 Interactive Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
