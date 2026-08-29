# PULSEiQ — AI/ML, Simulation, Graph & Optimization Modules

PULSEiQ is an AI-powered electricity grid simulation, risk analysis, and optimization platform. The `ai/` package provides modular, backend-independent Python engines that the FastAPI backend can consume.

---

## Architecture & Data Flow

```
Forecasting (ai.forecasting)
       │
       ▼  (Forecasted 24h demand & renewable curves)
Simulation (ai.simulation)
       │
       ▼  (Power flow, line flows, bus voltages, Monte Carlo LOLP/EUE)
Risk Analysis (ai.risk) & Graph Analytics (ai.graph)
       │
       ▼  (N-1 / N-k contingency screening, cascading failures, risk index)
Optimization (ai.optimization)
          (Optimal economic dispatch, battery scheduling, critical load protection)
```

---

## Approved Tech Stack

| Domain | Technologies Used |
|---|---|
| **AI / Machine Learning** | Scikit-learn, XGBoost, Pandas |
| **Simulation** | NumPy, SciPy, Monte Carlo |
| **Graph & Topology** | NetworkX |
| **Optimization** | SciPy Linear Programming / PuLP / OR-Tools |

---

## Submodule Overview

### 1. [`ai/forecasting/`](file:///c:/Users/hello/PULSEiQ/ai/forecasting)
- **`DemandForecaster`**: Multi-horizon load forecasting with uncertainty confidence bands ($10\% - 90\%$).
- **`SolarForecaster`**: Solar PV irradiance and thermal degradation modeling.
- **`WindForecaster`**: Aerodynamic turbine power curve response to Weibull wind fields.
- **`GridForecaster`**: Unified multi-asset system forecast orchestrator.

### 2. [`ai/simulation/`](file:///c:/Users/hello/PULSEiQ/ai/simulation)
- **`solve_power_flow`**: Linear DC power flow engine calculating branch active flows, line utilization, bus voltage profiles ($V_{pu}$), and frequency deviation ($\Delta f$).
- **`run_monte_carlo_simulation`**: Probabilistic simulator assessing Loss of Load Probability (LOLP) and Expected Unserved Energy (EUE MWh).

### 3. [`ai/risk/`](file:///c:/Users/hello/PULSEiQ/ai/risk)
- **`run_n_1_analysis`**: Exhaustive single line and generator contingency screening.
- **`run_n_k_analysis`**: Multi-asset outage combinatorial evaluation.
- **`simulate_cascading_failure`**: Sequential thermal overload tripping simulator.
- **`calculate_grid_risk_index`**: Standardized grid risk index ($0.0 \le \text{risk} \le 1.0$) and FastAPI-ready scorecard.

### 4. [`ai/graph/`](file:///c:/Users/hello/PULSEiQ/ai/graph)
- **`grid_to_networkx`**: Graph topology transformation preserving electrical and risk metadata.
- Dynamic graph topology manipulation (`add_grid_node`, `add_transmission_edge`, `remove_failed_line`, `remove_failed_node`).
- Centrality, bridge detection, cut vertices, and connected component analysis.

### 5. [`ai/optimization/`](file:///c:/Users/hello/PULSEiQ/ai/optimization)
- **`solve_optimal_dispatch`**: Constrained economic power dispatch solver.
- Renewable priority dispatch with curtailment minimization.
- BESS battery charge/discharge scheduling bounded by State of Charge.
- High-penalty critical load protection (hospitals, data centers).

---

## Verification & Testing

Run all unit tests:
```bash
python -m pytest tests/ -v
```
