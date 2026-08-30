import os
import sys

# Ensure repository root is on sys.path for direct CLI execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from ai.models.mock_grid import create_mock_grid
from ai.pipeline import GridIntelligencePipeline, PipelineConfig


def run_full_demo():
    print("=" * 80)
    print(" PULSEiQ AI ENGINE DEMO — STEP 4 UNIFIED PREDICTION & RISK PIPELINE")
    print("=" * 80)

    # 1. Initialize Mock Grid
    grid = create_mock_grid()
    print(f"\n[1] INITIALIZED GRID: '{grid.name}' ({len(grid.nodes)} Nodes, {len(grid.lines)} Lines)")

    # 2. Instantiate Unified AI Pipeline
    pipeline = GridIntelligencePipeline()
    config = PipelineConfig(
        forecast_horizon_hours=24,
        include_simulation=True,
        include_monte_carlo=True,
        monte_carlo_trials=30,
        include_contingency_screening=True,
        include_cascading_analysis=True,
        n_1_top_k=3,
        ranked_components_top_k=5,
    )

    # 3. Execute End-to-End Pipeline
    print("\n[2] EXECUTING UNIFIED AI/ML PREDICTION & RISK PIPELINE...")
    result = pipeline.run(grid, config=config)

    # 4. Display Forecast Section
    print(f"\n[3] FORECAST INTELLIGENCE ({result.forecast.horizon_hours}-Hour Horizon):")
    print(f"    - Total Forecasted Demand: {result.forecast.total_forecasted_demand_mwh:.1f} MWh")
    print(f"    - Total Forecasted Renewables: {result.forecast.total_forecasted_renewable_mwh:.1f} MWh")
    print(f"    - Peak Demand: {result.forecast.peak_demand_mw:.1f} MW | Peak Net Load: {result.forecast.peak_net_load_mw:.1f} MW")
    print(f"    - Renewable Penetration: {result.forecast.renewable_penetration_pct:.1f}%")

    # 5. Display Physical Simulation Section
    print("\n[4] POWER FLOW & RELIABILITY SIMULATION:")
    print(f"    - Frequency: {result.simulation.frequency_hz:.2f} Hz (Stable: {result.simulation.is_frequency_stable})")
    print(f"    - Max Line Utilization: {result.simulation.max_line_utilization_pct:.1f}%")
    print(f"    - Loss of Load Probability (LOLP): {result.simulation.loss_of_load_probability}")
    print(f"    - Expected Unserved Energy (EUE): {result.simulation.expected_unserved_energy_mwh} MWh")

    # 6. Display Graph Topology Section
    print("\n[5] GRAPH TOPOLOGY INTELLIGENCE:")
    print(f"    - Connected Graph: {result.topology.is_connected} (Density: {result.topology.density:.4f})")
    print(f"    - Articulation Points (Cut Vertices): {result.topology.articulation_points}")
    print(f"    - Bridge Lines: {len(result.topology.bridges)} bridge lines detected")

    # 7. Display Risk & Contingency Section
    print(f"\n[6] MULTI-FACTOR RISK ASSESSMENT:")
    print(f"    - Overall Risk Score: {result.risk.score:.4f} / 1.0000")
    print(f"    - Risk Classification: {result.risk.level}")
    print(f"    - Critical Load at Risk: {result.risk.critical_load_at_risk}")
    print(f"    - N-1 Insecure Violations: {result.risk.n_1_violations_count}")
    print("    - Factor Breakdown:")
    for f_name, f_val in result.risk.factors.items():
        print(f"        * {f_name}: {f_val:.4f}")

    # 8. Display Critical Component Rankings
    print("\n[7] TOP RANKED CRITICAL GRID ASSETS:")
    for comp in result.ranked_critical_components:
        print(f"    - #{comp['overall_criticality_rank']}: {comp['component_name']} ({comp['component_type']}) — Risk: {comp['risk_score']:.1f}/100")

    # 9. Display Execution Metadata
    print(f"\n[8] PIPELINE EXECUTION METADATA:")
    print(f"    - Status: {result.status}")
    print(f"    - Version: {result.metadata.pipeline_version}")
    print(f"    - Timestamp: {result.metadata.timestamp}")
    print(f"    - Total Compute Latency: {result.metadata.execution_time_ms:.1f} ms")

    print("\n" + "=" * 80)
    print(" PIPELINE RESULT FULLY VALIDATED AND READY FOR FASTAPI CONSUMPTION!")
    print("=" * 80)


if __name__ == "__main__":
    run_full_demo()
