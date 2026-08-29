# PULSEiQ — Simulation Module

## Overview
The `ai.simulation` module delivers steady-state power system simulation and probabilistic risk engines:
1. **DC / Linear Power Flow Solver**: Solves $B \theta = P$ using SciPy sparse/dense linear algebra, computing line flows, bus voltages, line utilization, and system frequency deviations.
2. **Monte Carlo Probabilistic Simulator**: Simulates thousands of stochastic states with renewable intermittency, customer demand fluctuations, and random component outage events.

---

## Inputs and Outputs

### Inputs
- `ElectricityGrid`: Grid topology, nodes, lines, and operational parameters.
- `iterations`: Number of Monte Carlo stochastic iterations (e.g. 500).
- `load_uncertainty_std`: Gaussian standard deviation for load variance.
- `renewable_uncertainty_std`: Gaussian standard deviation for renewable output.

### Outputs
- `SimulationResult`: Line loading status, branch power flows ($P_{ij}$ MW), bus voltage profiles ($V_{pu}$), frequency deviation ($\Delta f$ Hz), and unserved demand.
- `MonteCarloSummary`: Loss of Load Probability (LOLP), Expected Unserved Energy (EUE MWh), line overload probabilities, asset failure frequency distribution, and composite risk score.

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.simulation import solve_power_flow, run_monte_carlo_simulation

# Load grid
grid = create_mock_grid()

# 1. Single-State Power Flow
sim_result = solve_power_flow(grid)
print("Frequency (Hz):", sim_result.frequency_hz)
print("Max Line Utilization (%):", sim_result.max_line_utilization_pct)
print("Overloaded Lines:", sim_result.overloaded_lines_count)

# 2. Monte Carlo Probabilistic Simulation
mc_summary = run_monte_carlo_simulation(grid, iterations=500)
print("Loss of Load Probability (LOLP):", mc_summary.loss_of_load_probability)
print("Expected Unserved Energy (EUE MWh):", mc_summary.expected_unserved_energy_mwh)
print("Simulation Risk Score:", mc_summary.risk_score)
```
