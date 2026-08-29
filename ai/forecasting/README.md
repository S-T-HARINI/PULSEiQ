# PULSEiQ — Forecasting Module

## Overview
The `ai.forecasting` module delivers machine-learning-based time-series forecasting for:
1. **Electrical Load Demand (MW)** (Residential, Commercial, Industrial, and Critical Loads)
2. **Solar PV Generation (MW)** (Irradiance, temperature, and sun angle physics)
3. **Wind Power Generation (MW)** (Aerodynamic turbine power curves and Weibull gusts)

Leverages **XGBoost** and **Scikit-Learn** with probabilistic confidence interval bounds.

---

## Inputs and Outputs

### Inputs
- `GridNode`: Power grid asset with capacity and operational status.
- `horizon_hours`: Number of forward forecast hours (default: 24).
- `weather_df`: (Optional) Hourly ambient temperature, solar irradiance ($W/m^2$), and wind speed ($m/s$).

### Outputs
- `ForecastResult`: Single-asset hourly forecast series, peak MW, average MW, total MWh, and confidence bands.
- `GridForecastSummary`: System-wide aggregate demand curve, renewable generation curve, net load curve, and penetration statistics.

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.forecasting import GridForecaster

# Load test grid
grid = create_mock_grid()

# Instantiate unified forecaster
forecaster = GridForecaster()

# Run 24-hour multi-asset grid forecast
forecast_summary = forecaster.forecast_grid(grid, horizon_hours=24)

print("Peak Net Load (MW):", forecast_summary.peak_net_load_mw)
print("Total Demand (MWh):", forecast_summary.summary_metrics["total_demand_mwh"])
print("Renewable Penetration:", forecast_summary.summary_metrics["renewable_penetration_pct"], "%")
```
