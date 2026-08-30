# PULSEiQ — Risk Analysis Module

## Overview
The `ai.risk` module performs contingency screening, cascading thermal overload failure modeling, critical component ranking, and comprehensive multi-factor grid risk scoring for **PULSEiQ**.

---

## Key Features

1. **Standardized Risk Scale**:
   - `0.00 – 0.25`: **LOW**
   - `0.25 – 0.50`: **MODERATE**
   - `0.50 – 0.75`: **HIGH**
   - `0.75 – 1.00`: **CRITICAL**

2. **N-1 Contingency Analysis**:
   - Exhaustively evaluates all single-component outages:
     - Transmission lines (e.g. `N-1 Line Outage`)
     - Generators & renewable assets (e.g. `N-1 Generator Outage`)
     - Major substations & BESS storage units (e.g. `N-1 Major Component Outage`)
   - Computes affected components, post-trip connectivity, overloaded lines, critical load exposure, and severity ratings.

3. **N-k Contingency Foundation**:
   - `analyze_n_k(grid, failed_components, ...)` accepts an arbitrary list of failed component IDs.
   - Evaluates multi-component simultaneous outages with full topological isolation and power flow re-dispatch analysis.

4. **Cascading Failure Simulation**:
   - Explicitly tracks:
     - **Initial Failure**: Triggering trip event.
     - **Redistribution & Overloads**: Post-outage power flow causing secondary lines to exceed thermal thresholds ($> 115\%$).
     - **Secondary Failures**: Multi-stage sequential cascade propagation.
     - **Final State**: Network stabilization or partial/complete blackout.

5. **Dynamic Component Criticality Ranking**:
   - `rank_critical_components(grid)` dynamically computes importance scores combining betweenness centrality, line/generator loading, critical load path dependency, component failure probability ($p_{fail}$), and articulation/bridge status.

---

## Output Format (FastAPI Ready)

```json
{
  "risk_index": 0.455,
  "risk_level": "MODERATE",
  "failed_components": [],
  "affected_load_mw": 0.0,
  "critical_load_at_risk": true,
  "risk_factors": {
    "n1_contingency_insecurity": 0.2727,
    "transmission_loading": 0.7000,
    "critical_load_exposure": 1.0000,
    "generation_reserve_risk": 0.6628,
    "renewable_variability": 0.3556,
    "battery_storage_risk": 0.2150,
    "voltage_frequency_deviation": 0.0200
  },
  "n_1_violations_count": 3,
  "cascading_risk_score": 56.6,
  "most_critical_contingencies": [
    {
      "contingency_id": "N-1_gen_gas_01",
      "tripped_components": ["gen_gas_01"],
      "contingency_type": "N-1 Generator Outage",
      "is_secure": false,
      "unserved_load_mw": 0.0,
      "critical_load_at_risk": true,
      "severity": "MODERATE",
      "risk_score": 56.6
    }
  ],
  "ranked_critical_components": [
    {
      "component_id": "sub_trans_main",
      "component_name": "Central Bulk Transmission Substation (230kV/69kV)",
      "component_type": "substation",
      "risk_score": 95.0,
      "centrality_score": 0.8462,
      "critical_load_exposure_mw": 26.5,
      "is_articulation_point": true,
      "overall_criticality_rank": 1
    }
  ]
}
```

---

## Example Usage

```python
from ai.models.mock_grid import create_mock_grid
from ai.risk import (
    calculate_grid_risk_index,
    run_n_1_analysis,
    analyze_n_k,
    simulate_cascading_failure,
    rank_critical_components,
)

grid = create_mock_grid()

# 1. Multi-factor Risk Assessment
assessment = calculate_grid_risk_index(grid)
print("Risk Level:", assessment.risk_level.value)
print("Risk Index (0-1):", assessment.risk_index)

# 2. Ranked Critical Components
ranked = rank_critical_components(grid, top_n=5)
for comp in ranked:
    print(f"Rank #{comp.overall_criticality_rank}: {comp.component_name} (Score: {comp.risk_score})")

# 3. N-k Custom Failure Analysis
nk_res = analyze_n_k(grid, failed_components=["gen_gas_01", "line_submain_to_subsouth"])
print("N-k Secure:", nk_res.is_secure, "Severity:", nk_res.severity)

# 4. Cascading Failure Simulation
cascade = simulate_cascading_failure(grid, initial_trips=["line_submain_to_subsouth"])
print("Cascade Stages:", cascade.total_stages)
print("Secondary Failures:", cascade.secondary_failures)
```
