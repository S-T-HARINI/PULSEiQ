# PULSEiQ — Risk Analysis Module

## Overview
The `ai.risk` module performs contingency screening, cascading thermal failure modeling, and comprehensive grid risk scoring for **PULSEiQ**.

Key features:
1. **N-1 Contingency Analysis**: Exhaustive single-component outage screening (lines and generators).
2. **N-k Multi-Asset Screening**: Combinatorial multi-component failure screening.
3. **Cascading Failure Simulator**: Tracks sequential thermal overload line tripping until stabilization or system collapse.
4. **Grid Risk Scorecard**: Standardized risk scorecard designed for FastAPI backend consumption.

---

## Output Contract (FastAPI Ready)

```json
{
  "risk_index": 0.184,
  "risk_level": "LOW",
  "failed_components": [],
  "affected_load_mw": 0.0,
  "critical_load_at_risk": false,
  "n_1_violations_count": 0,
  "cascading_risk_score": 14.5,
  "most_critical_contingencies": [
    {
      "contingency_id": "N-1_line_submain_to_subsouth",
      "tripped_components": ["line_submain_to_subsouth"],
      "contingency_type": "N-1 Line Outage",
      "is_secure": true,
      "unserved_load_mw": 0.0,
      "critical_load_at_risk": false,
      "severity_score": 28.5
    }
  ]
}
```

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.risk import calculate_grid_risk_index, run_n_1_analysis, simulate_cascading_failure

grid = create_mock_grid()

# 1. Overall Grid Risk Index
risk_summary = calculate_grid_risk_index(grid)
print("Risk Level:", risk_summary.risk_level)
print("Risk Index (0-1):", risk_summary.risk_index)
print("Critical Load at Risk:", risk_summary.critical_load_at_risk)

# 2. N-1 Contingency Screen
top_n1 = run_n_1_analysis(grid, top_n_worst=5)
for c in top_n1:
    print(f"[{c.contingency_id}] Secure: {c.is_secure}, Severity: {c.severity_score}")

# 3. Cascading Failure Simulation
cascade = simulate_cascading_failure(grid, initial_trips=["line_submain_to_subnorth"])
print("Cascade Stages:", cascade.total_stages)
print("Blackout:", cascade.blackout_occurred)
```
