# PULSEiQ — Optimization Module

## Overview
The `ai.optimization` module formulates and solves **Optimal Economic Dispatch (ED)** and **Battery Energy Storage System (BESS) Scheduling** problems.

Key capabilities:
1. **Economic Dispatch**: Minimizes total generation costs while strictly matching demand across conventional and renewable generators.
2. **Renewable Priority Dispatch**: Dispatches zero-marginal-cost solar and wind first; manages curtailment when generation exceeds demand or transmission limits.
3. **BESS Optimal Scheduling**: Dynamically schedules battery charging (during solar/wind surplus or low demand) and discharging (during peak net load), respecting SoC upper/lower limits.
4. **Critical Load Protection**: Enforces heavy loss-of-load penalties on critical loads (hospitals, data centers) to guarantee priority service over normal residential/commercial loads.

---

## Inputs and Outputs

### Inputs
- `ElectricityGrid`: Network topology with active generators, renewable farms, batteries, and loads.
- `OptimizationConfig`: Fuel costs ($/MWh), battery degradation costs, and curtailment/load-shedding penalty multipliers.

### Outputs
- `DispatchResult`:
  - `status`: `OPTIMAL` / `FEASIBLE` / `INFEASIBLE`
  - `total_cost`: Objective function minimum ($)
  - `generator_dispatch_mw`: Dispatched MW per generator
  - `battery_dispatch_mw`: Discharged (+) or charged (-) MW per battery
  - `battery_soc_after_pct`: Updated State of Charge (%)
  - `curtailed_renewable_mw`: Curtailed renewable generation (MW)
  - `unserved_demand_mw`: Unserved demand per load node (MW)
  - `critical_load_served_pct`: Service percentage for critical loads (%)

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.optimization import solve_optimal_dispatch, OptimizationConfig

grid = create_mock_grid()

# Configure custom costs
config = OptimizationConfig(
    critical_load_shedding_penalty=20000.0,
    normal_load_shedding_penalty=500.0,
)

# Solve optimal dispatch
dispatch = solve_optimal_dispatch(grid, config=config)

print("Status:", dispatch.status)
print("Total Cost ($):", dispatch.total_cost)
print("Generator Dispatches (MW):", dispatch.generator_dispatch_mw)
print("Battery Dispatch (MW):", dispatch.battery_dispatch_mw)
print("Critical Load Served (%):", dispatch.critical_load_served_pct)
```
