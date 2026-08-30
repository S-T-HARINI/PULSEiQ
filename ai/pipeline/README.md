# PULSEiQ — Unified AI/ML Prediction & Risk Pipeline

## Overview
The `ai.pipeline` module provides the unified AI/ML orchestration layer for **PULSEiQ**. It coordinates the modular forecasting, power flow simulation, NetworkX graph intelligence, and risk assessment engines into a single standardized service: `GridIntelligencePipeline` (also aliased as `GridAIPipeline`).

---

## Architecture & Data Flow

```
                     ┌────────────────────────┐
                     │ Grid Model & Telemetry │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │ Input & Data Validator │
                     └───────────┬────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │                           │                           │
┌────▼─────────────┐   ┌─────────▼────────┐        ┌─────────▼────────┐
│   ai.forecasting │   │   ai.simulation  │        │     ai.graph     │
│  (Demand, Solar, │   │   (DC Power Flow,│        │(Centrality, Cut  │
│  Wind, Net Load) │   │ Droop Frequency) │        │Points, Bridges)  │
└────┬─────────────┘   └─────────┬────────┘        └─────────┬────────┘
     │                           │                           │
     └───────────────────────────┼───────────────────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │        ai.risk         │
                     │(Scorecard, N-1, Cascade│
                     │  Component Ranking)    │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │ GridIntelligenceResult │
                     │ (FastAPI JSON Payload) │
                     └────────────────────────┘
```

---

## Input Specification

### 1. `PipelineInput`
- `grid: ElectricityGrid`: Complete topological grid model containing buses, generators, renewables, substations, and lines.
- `telemetry: Optional[Dict[str, Any]]`: Real-time overrides for node demand/generation and line current flows.
- `config: PipelineConfig`: Execution settings.

### 2. `PipelineConfig`
- `forecast_horizon_hours: int` (Default: `24`): Number of hours to forecast.
- `include_simulation: bool` (Default: `True`): Run linear DC power flow.
- `include_monte_carlo: bool` (Default: `False`): Run probabilistic Monte Carlo trials.
- `monte_carlo_trials: int` (Default: `50`).
- `include_contingency_screening: bool` (Default: `True`): Screen N-1 outages.
- `include_cascading_analysis: bool` (Default: `True`): Run sequential thermal cascade simulation.
- `n_1_top_k: int` (Default: `5`): Top N-1 violations to include in output.
- `ranked_components_top_k: int` (Default: `5`): Top critical components to rank.

---

## Output Schema (`GridIntelligenceResult`)

```json
{
  "status": "SUCCESS",
  "forecast": {
    "horizon_hours": 24,
    "load_forecast_mw": [112.5, 108.2, "..."],
    "solar_forecast_mw": [0.0, 15.2, 42.0, "..."],
    "wind_forecast_mw": [28.4, 33.1, "..."],
    "net_load_forecast_mw": [84.1, 60.0, "..."],
    "total_forecasted_demand_mwh": 928.3,
    "total_forecasted_renewable_mwh": 570.4,
    "peak_demand_mw": 128.5,
    "peak_net_load_mw": 39.1,
    "renewable_penetration_pct": 61.4,
    "timestamps": ["2026-08-29T12:00:00+00:00", "..."],
    "time_series_points": [...]
  },
  "risk": {
    "score": 0.7857,
    "level": "CRITICAL",
    "factors": {
      "n1_contingency_insecurity": 1.0,
      "transmission_loading": 0.7,
      "critical_load_exposure": 1.0,
      "generation_reserve_risk": 0.6628,
      "renewable_variability": 0.3556,
      "battery_storage_risk": 0.215,
      "voltage_frequency_deviation": 1.0
    },
    "n_1_violations_count": 15,
    "critical_load_at_risk": true,
    "affected_load_mw": 0.0,
    "cascading_risk_score": 90.3,
    "most_critical_contingencies": [...]
  },
  "topology": {
    "node_count": 12,
    "edge_count": 12,
    "is_connected": true,
    "connected_components_count": 1,
    "density": 0.1818,
    "average_degree": 2.0,
    "critical_nodes": [...],
    "articulation_points": ["sub_trans_main", "sub_dist_north", "sub_dist_south"],
    "bridges": [["gen_gas_01", "sub_trans_main"], "..."],
    "isolated_nodes": [],
    "isolated_load_nodes": []
  },
  "simulation": {
    "power_flow_converged": true,
    "total_generation_mw": 135.0,
    "total_demand_mw": 128.5,
    "unserved_load_mw": 0.0,
    "frequency_hz": 60.01,
    "is_frequency_stable": true,
    "max_line_utilization_pct": 70.0,
    "overloaded_lines_count": 0
  },
  "ranked_critical_components": [...],
  "metadata": {
    "grid_id": "pulseiq_demo_grid_01",
    "grid_name": "PULSEiQ Regional Demonstration Grid",
    "timestamp": "2026-08-29T12:00:00.000000+00:00",
    "pipeline_version": "1.0.0",
    "execution_time_ms": 142.5
  }
}
```

---

## Python Usage Example

```python
from ai.models.mock_grid import create_mock_grid
from ai.pipeline import GridIntelligencePipeline, PipelineConfig

grid = create_mock_grid()
pipeline = GridIntelligencePipeline()

# Execute 24-hour prediction and risk evaluation
result = pipeline.run(
    grid=grid,
    config=PipelineConfig(forecast_horizon_hours=24),
)

print(f"Pipeline Status: {result.status}")
print(f"Risk Level: {result.risk.level} (Score: {result.risk.score:.4f})")
print(f"Forecast Demand: {result.forecast.total_forecasted_demand_mwh:.1f} MWh")
print(f"Execution Time: {result.metadata.execution_time_ms:.1f} ms")

# Serialize to JSON dict for FastAPI
json_payload = result.to_dict()
```

---

## Running Verification

```bash
# Run complete test suite
python -m pytest tests/ -v

# Run standalone end-to-end pipeline demo
python tests/demo_pipeline.py
```
