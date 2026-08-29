"""
PULSEiQ - Unified AI/ML Prediction & Risk Pipeline Orchestrator.
Coordinates Forecasting, Physical Simulation, Graph Topology Analytics,
and Multi-Factor Risk Assessment into a single unified service.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from ai.forecasting.forecaster import GridForecaster
from ai.forecasting.models import GridForecastSummary
from ai.graph.builder import analyze_graph_topology, grid_to_networkx
from ai.models.grid import ElectricityGrid
from ai.pipeline.models import (
    ForecastSection,
    GridIntelligenceResult,
    PipelineConfig,
    PipelineInput,
    PipelineMetadata,
    RiskSection,
    SimulationSection,
    TopologySection,
)
from ai.pipeline.validator import PipelineValidationError, validate_pipeline_input
from ai.risk.contingency import (
    calculate_grid_risk_index,
    rank_critical_components,
    run_n_1_analysis,
    simulate_cascading_failure,
)
from ai.simulation.monte_carlo import run_monte_carlo_simulation
from ai.simulation.power_flow import solve_power_flow


class GridIntelligencePipeline:
    """
    Unified AI/ML orchestration service for PULSEiQ.
    Coordinates all modular AI capabilities without duplicating internal logic:
      1. Telemetry & Input Data Validation
      2. Multi-Asset Time-Series Forecasting (Demand, Solar, Wind, Net Load)
      3. Physical Grid Power Flow Simulation & Droop Frequency Stability
      4. NetworkX Topological & Connectivity Analysis
      5. Multi-Factor Risk Scorecard, N-1 Screening & Cascading Failures
    """

    def __init__(self, forecaster: Optional[GridForecaster] = None):
        """Initialize pipeline with modular components."""
        self.forecaster = forecaster or GridForecaster()

    def run(
        self,
        grid_or_input: Union[ElectricityGrid, PipelineInput],
        config: Optional[PipelineConfig] = None,
        telemetry: Optional[Dict[str, Any]] = None,
    ) -> GridIntelligenceResult:
        """
        Executes the end-to-end unified AI/ML intelligence and risk pipeline.

        Args:
            grid_or_input: ElectricityGrid instance or wrapped PipelineInput.
            config: (Optional) PipelineConfig overriding defaults.
            telemetry: (Optional) Live telemetry readings to merge into operational state.

        Returns:
            GridIntelligenceResult: Structured, type-safe result ready for API serialization.

        Raises:
            PipelineValidationError: If input data or parameters are invalid.
        """
        start_time = time.perf_counter()

        # 1. Normalize and Validate Input
        if isinstance(grid_or_input, PipelineInput):
            pipeline_input = grid_or_input
            if config is not None:
                pipeline_input.config = config
            if telemetry is not None:
                pipeline_input.telemetry = telemetry
        elif isinstance(grid_or_input, ElectricityGrid):
            pipeline_input = PipelineInput(
                grid=grid_or_input,
                config=config or PipelineConfig(),
                telemetry=telemetry,
                timestamp=datetime.now(timezone.utc),
            )
        else:
            raise PipelineValidationError(
                f"Expected ElectricityGrid or PipelineInput, got {type(grid_or_input).__name__}.",
                field_name="grid_or_input",
            )

        validate_pipeline_input(pipeline_input)

        grid = pipeline_input.grid
        cfg = pipeline_input.config

        # 2. Merge Telemetry if supplied
        if pipeline_input.telemetry:
            grid = self._apply_telemetry(grid, pipeline_input.telemetry)

        # 3. Stage 1: Forecasting Integration
        forecast_section = self._run_forecasting_stage(grid, cfg.forecast_horizon_hours)

        # 4. Stage 2: Physical Simulation Integration
        sim_section = self._run_simulation_stage(grid, cfg)

        # 5. Stage 3: Graph Topology Integration
        graph_obj = grid_to_networkx(grid)
        topology_section = self._run_topology_stage(grid, graph_obj)

        # 6. Stage 4: Risk & Contingency Assessment Integration
        risk_section, ranked_components = self._run_risk_stage(grid, graph_obj, cfg)

        # 7. Metadata & Timing
        execution_time_ms = (time.perf_counter() - start_time) * 1000.0
        now_iso = (pipeline_input.timestamp or datetime.now(timezone.utc)).isoformat()

        metadata = PipelineMetadata(
            grid_id=grid.grid_id,
            grid_name=grid.name,
            timestamp=now_iso,
            pipeline_version="1.0.0",
            execution_time_ms=execution_time_ms,
        )

        return GridIntelligenceResult(
            status="SUCCESS",
            forecast=forecast_section,
            risk=risk_section,
            topology=topology_section,
            simulation=sim_section,
            ranked_critical_components=ranked_components,
            metadata=metadata,
        )

    def _apply_telemetry(self, grid: ElectricityGrid, telemetry: Dict[str, Any]) -> ElectricityGrid:
        """Applies live telemetry overrides to a deep copy of the grid."""
        import copy
        grid_copy = copy.deepcopy(grid)

        if "nodes" in telemetry and isinstance(telemetry["nodes"], dict):
            for nid, node_data in telemetry["nodes"].items():
                if nid in grid_copy.nodes:
                    target_node = grid_copy.nodes[nid]
                    if "demand_mw" in node_data:
                        target_node.operational.demand_mw = float(node_data["demand_mw"])
                    if "generation_mw" in node_data:
                        target_node.operational.generation_mw = float(node_data["generation_mw"])
                    if "voltage_kv" in node_data:
                        target_node.operational.voltage_kv = float(node_data["voltage_kv"])

        if "lines" in telemetry and isinstance(telemetry["lines"], dict):
            for lid, line_data in telemetry["lines"].items():
                if lid in grid_copy.lines:
                    target_line = grid_copy.lines[lid]
                    if "current_flow_mw" in line_data:
                        target_line.current_flow_mw = float(line_data["current_flow_mw"])

        return grid_copy

    def _run_forecasting_stage(self, grid: ElectricityGrid, horizon_hours: int) -> ForecastSection:
        """Executes unified 24h demand, solar, and wind forecasts."""
        fc_summary: GridForecastSummary = self.forecaster.forecast_grid(grid, horizon_hours=horizon_hours)

        load_curve = list(fc_summary.total_demand_curve)
        net_load_curve = list(fc_summary.net_load_curve)
        timestamps = list(fc_summary.timestamps)

        # Aggregate solar curve across all solar assets
        if fc_summary.solar_forecasts:
            solar_curve = [
                sum(res.points[h].value_mw for res in fc_summary.solar_forecasts.values() if h < len(res.points))
                for h in range(horizon_hours)
            ]
        else:
            solar_curve = [0.0] * horizon_hours

        # Aggregate wind curve across all wind assets
        if fc_summary.wind_forecasts:
            wind_curve = [
                sum(res.points[h].value_mw for res in fc_summary.wind_forecasts.values() if h < len(res.points))
                for h in range(horizon_hours)
            ]
        else:
            wind_curve = [0.0] * horizon_hours

        total_demand_mwh = float(fc_summary.summary_metrics.get("total_demand_mwh", sum(load_curve)))
        total_renewable_mwh = float(fc_summary.summary_metrics.get("total_renewable_mwh", sum(fc_summary.total_renewable_curve)))
        peak_demand_mw = float(fc_summary.summary_metrics.get("peak_demand_mw", max(load_curve) if load_curve else 0.0))
        peak_net_load_mw = float(fc_summary.peak_net_load_mw)
        ren_penetration_pct = float(fc_summary.summary_metrics.get("renewable_penetration_pct", 0.0))

        time_series_points = []
        for i in range(horizon_hours):
            time_series_points.append({
                "hour": i + 1,
                "timestamp": timestamps[i] if i < len(timestamps) else f"T+{i+1}h",
                "demand_mw": load_curve[i] if i < len(load_curve) else 0.0,
                "solar_mw": solar_curve[i] if i < len(solar_curve) else 0.0,
                "wind_mw": wind_curve[i] if i < len(wind_curve) else 0.0,
                "net_load_mw": net_load_curve[i] if i < len(net_load_curve) else 0.0,
            })

        return ForecastSection(
            horizon_hours=horizon_hours,
            load_forecast_mw=load_curve,
            solar_forecast_mw=solar_curve,
            wind_forecast_mw=wind_curve,
            net_load_forecast_mw=net_load_curve,
            total_forecasted_demand_mwh=total_demand_mwh,
            total_forecasted_renewable_mwh=total_renewable_mwh,
            peak_demand_mw=peak_demand_mw,
            peak_net_load_mw=peak_net_load_mw,
            renewable_penetration_pct=ren_penetration_pct,
            timestamps=timestamps,
            time_series_points=time_series_points,
        )

    def _run_simulation_stage(self, grid: ElectricityGrid, cfg: PipelineConfig) -> SimulationSection:
        """Executes physical power flow and optional Monte Carlo simulation."""
        sim_res = solve_power_flow(grid)

        lolp: Optional[float] = None
        eue: Optional[float] = None

        if cfg.include_monte_carlo:
            mc_res = run_monte_carlo_simulation(grid, iterations=cfg.monte_carlo_trials)
            lolp = mc_res.loss_of_load_probability
            eue = mc_res.expected_unserved_energy_mwh

        return SimulationSection(
            power_flow_converged=True,
            total_generation_mw=sim_res.total_generation_mw,
            total_demand_mw=sim_res.total_demand_mw,
            unserved_load_mw=sim_res.unserved_load_mw,
            frequency_hz=sim_res.frequency_hz,
            is_frequency_stable=sim_res.is_frequency_stable,
            max_line_utilization_pct=sim_res.max_line_utilization_pct,
            overloaded_lines_count=sim_res.overloaded_lines_count,
            loss_of_load_probability=lolp,
            expected_unserved_energy_mwh=eue,
        )

    def _run_topology_stage(self, grid: ElectricityGrid, graph_obj: Any) -> TopologySection:
        """Extracts NetworkX topological parameters and cut points."""
        top_analysis = analyze_graph_topology(graph_obj, grid=grid)

        return TopologySection(
            node_count=top_analysis.node_count,
            edge_count=top_analysis.edge_count,
            is_connected=top_analysis.is_connected,
            connected_components_count=top_analysis.connected_components_count,
            density=top_analysis.density,
            average_degree=top_analysis.average_degree,
            critical_nodes=top_analysis.critical_hubs,
            articulation_points=top_analysis.articulation_points,
            bridges=[list(b) for b in top_analysis.bridges],
            isolated_nodes=top_analysis.isolated_nodes,
            isolated_load_nodes=top_analysis.isolated_load_nodes,
        )

    def _run_risk_stage(
        self,
        grid: ElectricityGrid,
        graph_obj: Any,
        cfg: PipelineConfig,
    ) -> tuple[RiskSection, List[Dict[str, Any]]]:
        """Computes multi-factor risk scorecard, N-1 contingencies, and critical rankings."""
        assessment = calculate_grid_risk_index(grid)
        ranked_components = rank_critical_components(
            grid,
            graph=graph_obj,
            top_n=cfg.ranked_components_top_k,
        )

        n1_results = []
        if cfg.include_contingency_screening:
            n1_list = run_n_1_analysis(grid, top_n_worst=cfg.n_1_top_k)
            n1_results = [c.to_dict() for c in n1_list]

        cascade_dict = None
        if cfg.include_cascading_analysis:
            # Trigger line: use config trigger or default to most heavily loaded bridge line
            trigger_lines = cfg.cascading_trigger_lines
            if not trigger_lines:
                # Pick highest utilized line
                lines_by_util = sorted(grid.lines.values(), key=lambda l: l.utilization_pct, reverse=True)
                if lines_by_util:
                    trigger_lines = [lines_by_util[0].id]

            if trigger_lines:
                cascade_report = simulate_cascading_failure(grid, initial_trips=trigger_lines)
                cascade_dict = cascade_report.to_dict()

        risk_section = RiskSection(
            score=assessment.risk_index,
            level=assessment.risk_level.value,
            factors=assessment.risk_factors,
            n_1_violations_count=assessment.n_1_violations_count,
            critical_load_at_risk=assessment.critical_load_at_risk,
            affected_load_mw=assessment.affected_load_mw,
            cascading_risk_score=assessment.cascading_risk_score,
            most_critical_contingencies=n1_results,
            cascading_report=cascade_dict,
        )

        ranked_dict_list = [rc.to_dict() for rc in ranked_components]

        return risk_section, ranked_dict_list


# Reusable alias
GridAIPipeline = GridIntelligencePipeline
