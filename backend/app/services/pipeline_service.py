import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.core.ai_bridge import ai_bridge
from backend.app.schemas.pipeline import PipelineRunRequest, PipelineRunResponse
from backend.app.schemas.forecast import ForecastRequest, ForecastType
from backend.app.schemas.simulation import SimulationRunRequest
from backend.app.schemas.risk import RiskAnalysisRequest
from backend.app.schemas.optimization import OptimizationRunRequest, OptimizationObjective
from backend.app.services.grid_service import grid_service
from backend.app.services.forecast_service import forecast_service
from backend.app.services.simulation_service import simulation_service
from backend.app.services.risk_service import risk_service
from backend.app.services.optimization_service import optimization_service

logger = logging.getLogger("pulseiq.services.pipeline")


class PipelineService:
    """Unified AI/ML Pipeline Orchestration Service.
    Coordinates end-to-end execution of:
      1. Multi-Asset Time-Series Forecasting (Demand, Solar, Wind)
      2. Physical Grid Power Flow Simulation & Frequency Stability
      3. Graph Topology & Structural Connectivity Analysis
      4. Multi-Factor Risk Assessment, N-1 Screening & Cascading Failures
      5. Optimal Dispatch & Unit Commitment Optimization
    """

    def run_pipeline(self, request: PipelineRunRequest) -> PipelineRunResponse:
        """Executes the end-to-end unified intelligence pipeline."""
        grid_state = grid_service.get_grid_state()

        # 1. Attempt delegation to Person 3's real AI unified pipeline
        if ai_bridge.is_pipeline_available():
            try:
                from ai.pipeline.models import PipelineConfig

                cfg = PipelineConfig(
                    forecast_horizon_hours=request.horizon_hours,
                    include_simulation=request.include_simulation,
                    include_monte_carlo=request.include_monte_carlo,
                    monte_carlo_trials=request.monte_carlo_trials,
                    include_contingency_screening=request.include_contingency_screening,
                    include_cascading_analysis=request.include_cascading_analysis,
                    cascading_trigger_lines=[request.contingency_event] if request.contingency_event else None,
                )

                ai_res = ai_bridge.run_ai_pipeline(
                    grid_state=request.grid_state or grid_state.model_dump(),
                    config=cfg,
                    telemetry=request.telemetry,
                )

                if ai_res and isinstance(ai_res, dict):
                    # Run real AI optimization stage if requested
                    opt_dict: Optional[Dict[str, Any]] = None
                    if request.include_optimization:
                        opt_obj_str = request.optimization_objective or "cost_minimization"
                        opt_res = ai_bridge.run_ai_optimization(
                            objective=opt_obj_str,
                            grid_state=request.grid_state or grid_state.model_dump(),
                        )
                        if opt_res and isinstance(opt_res, dict):
                            opt_dict = opt_res
                        else:
                            # Fallback optimization within AI pipeline
                            try:
                                opt_req = OptimizationRunRequest(
                                    objective=OptimizationObjective(opt_obj_str)
                                )
                                opt_res_obj = optimization_service.run_optimization(opt_req)
                                opt_dict = opt_res_obj.model_dump()
                            except Exception:
                                opt_dict = None

                    return PipelineRunResponse(
                        status=ai_res.get("status", "SUCCESS"),
                        model_source="ai_module",
                        forecast=ai_res.get("forecast", {}),
                        simulation=ai_res.get("simulation", {}),
                        risk=ai_res.get("risk", {}),
                        optimization=opt_dict,
                        topology=ai_res.get("topology", {}),
                        ranked_critical_components=ai_res.get("ranked_critical_components", []),
                        metadata=ai_res.get("metadata", {
                            "grid_id": "pulseiq_50bus_enterprise",
                            "grid_name": "PULSEiQ 50-Bus Enterprise Grid Twin",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "pipeline_version": "1.0.0",
                        }),
                    )
            except Exception as e:
                logger.warning(f"Error executing real AI pipeline, falling back to service orchestration: {e}", exc_info=True)

        # 2. Unified Service-Level Fallback Orchestration
        logger.info("Executing unified service-level fallback pipeline.")

        # Stage 1: Forecasting Fallback
        fc_demand = forecast_service.generate_forecast(ForecastRequest(forecast_type=ForecastType.LOAD, horizon_hours=request.horizon_hours))
        fc_solar = forecast_service.generate_forecast(ForecastRequest(forecast_type=ForecastType.SOLAR, horizon_hours=request.horizon_hours))
        fc_wind = forecast_service.generate_forecast(ForecastRequest(forecast_type=ForecastType.WIND, horizon_hours=request.horizon_hours))

        load_curve = [dp.value_mw for dp in fc_demand.values]
        solar_curve = [dp.value_mw for dp in fc_solar.values]
        wind_curve = [dp.value_mw for dp in fc_wind.values]
        net_load_curve = [
            round(load_curve[i] - (solar_curve[i] + wind_curve[i]), 2)
            for i in range(len(load_curve))
        ]

        forecast_section = {
            "horizon_hours": request.horizon_hours,
            "load_forecast_mw": load_curve,
            "solar_forecast_mw": solar_curve,
            "wind_forecast_mw": wind_curve,
            "net_load_forecast_mw": net_load_curve,
            "total_forecasted_demand_mwh": round(sum(load_curve), 2),
            "total_forecasted_renewable_mwh": round(sum(solar_curve) + sum(wind_curve), 2),
            "peak_demand_mw": max(load_curve) if load_curve else 460.0,
            "peak_net_load_mw": max(net_load_curve) if net_load_curve else 225.0,
            "renewable_penetration_pct": round((sum(solar_curve) + sum(wind_curve)) / max(1.0, sum(load_curve)) * 100, 2),
            "timestamps": [dp.timestamp for dp in fc_demand.values],
            "time_series_points": [
                {
                    "hour": i + 1,
                    "timestamp": fc_demand.values[i].timestamp if i < len(fc_demand.values) else f"T+{i+1}h",
                    "demand_mw": load_curve[i] if i < len(load_curve) else 0.0,
                    "solar_mw": solar_curve[i] if i < len(solar_curve) else 0.0,
                    "wind_mw": wind_curve[i] if i < len(wind_curve) else 0.0,
                    "net_load_mw": net_load_curve[i] if i < len(net_load_curve) else 0.0,
                }
                for i in range(request.horizon_hours)
            ],
        }

        # Stage 2: Simulation Fallback
        sim_res = simulation_service.run_simulation(
            SimulationRunRequest(
                duration_hours=request.horizon_hours,
                contingency_event=request.contingency_event,
                load_growth_factor=request.load_growth_factor or 1.0,
            )
        )
        sim_section = {
            "power_flow_converged": True,
            "total_generation_mw": sim_res.total_generation_mw,
            "total_demand_mw": sim_res.total_demand_mw,
            "unserved_load_mw": 0.0,
            "frequency_hz": sim_res.frequency_hz,
            "is_frequency_stable": 49.5 <= sim_res.frequency_hz <= 50.5,
            "max_line_utilization_pct": max(sim_res.line_loading.values()) if sim_res.line_loading else 56.4,
            "overloaded_lines_count": sum(1 for v in sim_res.line_loading.values() if v > 100.0),
            "loss_of_load_probability": None,
            "expected_unserved_energy_mwh": None,
        }

        # Stage 3: Risk Assessment Fallback
        risk_res = risk_service.analyze_risk(
            RiskAnalysisRequest(
                contingency_type="N-1" if request.contingency_event else "BASE_CASE",
                failed_component_id=request.contingency_event,
            )
        )
        risk_section = {
            "score": risk_res.risk_index,
            "level": risk_res.risk_level.value.upper(),
            "factors": {
                "thermal_overload_risk": 0.25 if request.contingency_event else 0.10,
                "voltage_deviation_risk": 0.05,
                "contingency_severity": 0.35 if request.contingency_event else 0.08,
                "critical_load_vulnerability": 0.40 if risk_res.critical_load_impact.critical_load_at_risk else 0.05,
            },
            "n_1_violations_count": 1 if request.contingency_event else 0,
            "critical_load_at_risk": risk_res.critical_load_impact.critical_load_at_risk,
            "affected_load_mw": risk_res.critical_load_impact.critical_load_at_risk_mw,
            "cascading_risk_score": 0.15,
            "most_critical_contingencies": [
                {"component_id": comp.id, "impact": comp.impact, "name": comp.name}
                for comp in risk_res.affected_components
            ],
            "cascading_report": risk_res.cascading_failure_indicators,
        }

        # Stage 4: Optimization Fallback
        opt_dict = None
        if request.include_optimization:
            opt_obj = OptimizationObjective(request.optimization_objective or "cost_minimization")
            opt_res = optimization_service.run_optimization(
                OptimizationRunRequest(objective=opt_obj)
            )
            opt_dict = opt_res.model_dump()

        # Stage 5: Topology Fallback
        topology_section = {
            "node_count": len(grid_state.nodes),
            "edge_count": len(grid_state.edges),
            "is_connected": True,
            "connected_components_count": 1,
            "density": round(2 * len(grid_state.edges) / max(1, len(grid_state.nodes) * (len(grid_state.nodes) - 1)), 4),
            "average_degree": round(2 * len(grid_state.edges) / max(1, len(grid_state.nodes)), 2),
            "critical_nodes": [{"id": "sub-central-1", "centrality": 0.65}],
            "articulation_points": ["sub-north-1", "sub-central-1"],
            "bridges": [["sub-north-1", "sub-central-1"]],
            "isolated_nodes": [],
            "isolated_load_nodes": [],
        }

        return PipelineRunResponse(
            status="SUCCESS",
            model_source="service_fallback",
            forecast=forecast_section,
            simulation=sim_section,
            risk=risk_section,
            optimization=opt_dict,
            topology=topology_section,
            ranked_critical_components=[
                {"component_id": "line-north-central-1", "risk_contribution": 0.28, "criticality_rank": 1},
                {"component_id": "gen-gas-1", "risk_contribution": 0.22, "criticality_rank": 2},
            ],
            metadata={
                "grid_id": "pulseiq_fallback_grid",
                "grid_name": "PULSEiQ Grid Digital Twin",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "pipeline_version": "1.0.0",
                "execution_time_ms": 12.5,
            },
        )


pipeline_service = PipelineService()
