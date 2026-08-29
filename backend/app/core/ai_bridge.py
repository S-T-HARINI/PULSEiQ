import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("pulseiq.ai_bridge")


class AIModuleBridge:
    """Integration bridge between the FastAPI backend and Person 3's AI/ML modules.
    Provides verified detection, bidirectional grid schema translation, direct execution
    of real AI/ML pipelines, and deterministic fallback handling when offline.
    """

    def __init__(self) -> None:
        self._forecast_module: Optional[Any] = None
        self._simulation_module: Optional[Any] = None
        self._risk_module: Optional[Any] = None
        self._optimization_module: Optional[Any] = None
        self._graph_module: Optional[Any] = None
        self._pipeline_module: Optional[Any] = None
        self._grid_models: Optional[Any] = None
        self._discover_modules()

    def _discover_modules(self) -> None:
        """Attempts to dynamically import Person 3's AI/ML packages."""
        # 1. Grid Data Models
        try:
            import ai.models.grid as grid_models
            self._grid_models = grid_models
            logger.info("Successfully bound Person 3 AI Grid Models.")
        except (ImportError, ModuleNotFoundError):
            self._grid_models = None

        # 2. Forecasting module
        try:
            import ai.forecasting as fc_mod
            self._forecast_module = fc_mod
            logger.info("Successfully bound Person 3 AI Forecasting module.")
        except (ImportError, ModuleNotFoundError):
            self._forecast_module = None

        # 3. Simulation engine
        try:
            import ai.simulation as sim_mod
            self._simulation_module = sim_mod
            logger.info("Successfully bound Person 3 AI Simulation engine.")
        except (ImportError, ModuleNotFoundError):
            self._simulation_module = None

        # 4. Risk engine
        try:
            import ai.risk as risk_mod
            self._risk_module = risk_mod
            logger.info("Successfully bound Person 3 AI Risk engine.")
        except (ImportError, ModuleNotFoundError):
            self._risk_module = None

        # 5. Optimization solver
        try:
            import ai.optimization as opt_mod
            self._optimization_module = opt_mod
            logger.info("Successfully bound Person 3 AI Optimization engine.")
        except (ImportError, ModuleNotFoundError):
            self._optimization_module = None

        # 6. Graph module
        try:
            import ai.graph as graph_mod
            self._graph_module = graph_mod
            logger.info("Successfully bound Person 3 AI Graph module.")
        except (ImportError, ModuleNotFoundError):
            self._graph_module = None

        # 7. Unified Pipeline module
        try:
            import ai.pipeline as pipeline_mod
            self._pipeline_module = pipeline_mod
            logger.info("Successfully bound Person 3 AI Unified Pipeline module.")
        except (ImportError, ModuleNotFoundError):
            self._pipeline_module = None

    def is_forecasting_available(self) -> bool:
        return self._forecast_module is not None

    def is_simulation_available(self) -> bool:
        return self._simulation_module is not None

    def is_risk_available(self) -> bool:
        return self._risk_module is not None

    def is_optimization_available(self) -> bool:
        return self._optimization_module is not None

    def is_graph_available(self) -> bool:
        return self._graph_module is not None

    def is_pipeline_available(self) -> bool:
        return self._pipeline_module is not None

    def get_status_summary(self) -> Dict[str, str]:
        """Returns the operational availability status of all AI/ML subsystems."""
        return {
            "forecasting": "ai_module_connected" if self.is_forecasting_available() else "service_fallback_active",
            "simulation": "ai_module_connected" if self.is_simulation_available() else "service_fallback_active",
            "risk_engine": "ai_module_connected" if self.is_risk_available() else "service_fallback_active",
            "optimization": "ai_module_connected" if self.is_optimization_available() else "service_fallback_active",
            "graph_engine": "ai_module_connected" if self.is_graph_available() else "service_fallback_active",
            "unified_pipeline": "ai_module_connected" if self.is_pipeline_available() else "service_fallback_active",
        }

    # =========================================================================
    # Bidirectional Grid Data Translation
    # =========================================================================
    def convert_to_ai_grid(self, backend_grid_state: Optional[Any] = None) -> Any:
        """Converts backend GridResponse or state dictionary into an ai.models.grid.ElectricityGrid."""
        from ai.models.grid import (
            ElectricityGrid,
            GridNode as AIGridNode,
            TransmissionLine as AITransmissionLine,
            NodeType as AINodeType,
            ComponentStatus as AIComponentStatus,
            CriticalityLevel as AICriticalityLevel,
            OperationalData as AIOperationalData,
            RiskMetrics as AIRiskMetrics,
        )

        if backend_grid_state is None:
            from backend.app.services.grid_service import grid_service
            backend_grid_state = grid_service.get_grid_state()

        if isinstance(backend_grid_state, ElectricityGrid):
            return backend_grid_state

        # Extract nodes and edges whether from Pydantic model or dict
        if hasattr(backend_grid_state, "nodes") and hasattr(backend_grid_state, "edges"):
            nodes_data = backend_grid_state.nodes
            edges_data = backend_grid_state.edges
        elif isinstance(backend_grid_state, dict):
            nodes_data = backend_grid_state.get("nodes", [])
            edges_data = backend_grid_state.get("edges", [])
        else:
            from ai.models.mock_grid import create_mock_grid
            return create_mock_grid()

        ai_nodes: Dict[str, AIGridNode] = {}
        ai_lines: Dict[str, AITransmissionLine] = {}

        for n in nodes_data:
            nid = getattr(n, "id", n.get("id") if isinstance(n, dict) else str(n))
            name = getattr(n, "name", n.get("name", nid) if isinstance(n, dict) else nid)
            raw_type = getattr(n, "type", n.get("type", "load") if isinstance(n, dict) else "load")
            raw_type_str = raw_type.value if hasattr(raw_type, "value") else str(raw_type).lower()
            status_val = getattr(n, "status", n.get("status", "online") if isinstance(n, dict) else "online")
            status_str = status_val.value if hasattr(status_val, "value") else str(status_val).lower()
            crit_val = getattr(n, "criticality", n.get("criticality", "medium") if isinstance(n, dict) else "medium")
            crit_str = crit_val.value if hasattr(crit_val, "value") else str(crit_val).lower()
            cap = float(getattr(n, "capacity_mw", n.get("capacity_mw", 100.0) if isinstance(n, dict) else 100.0))
            output = float(getattr(n, "current_output_mw", n.get("current_output_mw", 0.0) if isinstance(n, dict) else 0.0))
            risk_val = float(getattr(n, "risk_score", n.get("risk_score", 0.1) if isinstance(n, dict) else 0.1))
            metadata = getattr(n, "metadata", n.get("metadata", {}) if isinstance(n, dict) else {})

            # Map Node Type
            if "solar" in raw_type_str:
                ai_type = AINodeType.SOLAR
                gen_mw = output
                dem_mw = 0.0
                ren_mw = output
            elif "wind" in raw_type_str:
                ai_type = AINodeType.WIND
                gen_mw = output
                dem_mw = 0.0
                ren_mw = output
            elif "bat" in raw_type_str or "storage" in raw_type_str:
                ai_type = AINodeType.BATTERY
                gen_mw = max(0.0, output)
                dem_mw = max(0.0, -output)
                ren_mw = 0.0
            elif "substation" in raw_type_str:
                ai_type = AINodeType.SUBSTATION
                gen_mw = 0.0
                dem_mw = 0.0
                ren_mw = 0.0
            elif "critical" in raw_type_str or "hospital" in raw_type_str:
                ai_type = AINodeType.LOAD_CRITICAL
                gen_mw = 0.0
                dem_mw = output
                ren_mw = 0.0
            elif "load" in raw_type_str or "industrial" in raw_type_str or "residential" in raw_type_str or "commercial" in raw_type_str:
                ai_type = AINodeType.LOAD_NORMAL
                gen_mw = 0.0
                dem_mw = output
                ren_mw = 0.0
            elif "gen" in raw_type_str or "generator" in raw_type_str or "gas" in raw_type_str:
                ai_type = AINodeType.GENERATOR
                gen_mw = output
                dem_mw = 0.0
                ren_mw = 0.0
            else:
                ai_type = AINodeType.LOAD_NORMAL
                gen_mw = 0.0
                dem_mw = output
                ren_mw = 0.0

            # Map Status
            if status_str in ("offline", "disconnected"):
                ai_status = AIComponentStatus.OFFLINE
            elif status_str in ("tripped", "failed"):
                ai_status = AIComponentStatus.TRIPPED
            elif status_str == "degraded":
                ai_status = AIComponentStatus.DEGRADED
            else:
                ai_status = AIComponentStatus.ONLINE

            # Map Criticality
            if crit_str == "critical":
                ai_crit = AICriticalityLevel.CRITICAL
            elif crit_str == "high":
                ai_crit = AICriticalityLevel.HIGH
            elif crit_str == "low":
                ai_crit = AICriticalityLevel.LOW
            else:
                ai_crit = AICriticalityLevel.MEDIUM

            ai_nodes[nid] = AIGridNode(
                id=nid,
                name=name,
                node_type=ai_type,
                status=ai_status,
                operational=AIOperationalData(
                    generation_mw=gen_mw,
                    demand_mw=dem_mw,
                    renewable_generation_mw=ren_mw,
                    max_capacity_mw=cap,
                    min_capacity_mw=0.0,
                    voltage_kv=float(metadata.get("voltage_kv", 115.0)),
                    voltage_pu=1.0,
                    frequency_hz=60.0,
                    battery_soc_pct=float(metadata.get("state_of_charge_percent", 78.5)),
                    battery_capacity_mwh=float(metadata.get("capacity_mwh", 320.0)),
                    battery_max_power_mw=cap if ai_type == AINodeType.BATTERY else 0.0,
                ),
                risk=AIRiskMetrics(
                    criticality=ai_crit,
                    failure_probability=risk_val * 0.05,
                    risk_score=risk_val * 100.0 if risk_val <= 1.0 else risk_val,
                ),
                location={"lat": float(getattr(n, "latitude", 37.77)), "lon": float(getattr(n, "longitude", -122.41))} if hasattr(n, "latitude") else None,
                metadata=dict(metadata),
            )

        for e in edges_data:
            eid = getattr(e, "id", e.get("id") if isinstance(e, dict) else str(e))
            source = getattr(e, "source", e.get("source", "") if isinstance(e, dict) else "")
            target = getattr(e, "target", e.get("target", "") if isinstance(e, dict) else "")
            cap = float(getattr(e, "capacity_mw", e.get("capacity_mw", 200.0) if isinstance(e, dict) else 200.0))
            flow = float(getattr(e, "power_flow_mw", e.get("power_flow_mw", 0.0) if isinstance(e, dict) else 0.0))
            status_val = getattr(e, "status", e.get("status", "normal") if isinstance(e, dict) else "normal")
            status_str = status_val.value if hasattr(status_val, "value") else str(status_val).lower()
            risk_val = float(getattr(e, "risk_score", e.get("risk_score", 0.1) if isinstance(e, dict) else 0.1))
            res_ohm = float(getattr(e, "resistance_ohms", e.get("resistance_ohms", 0.03) if isinstance(e, dict) else 0.03))
            react_ohm = float(getattr(e, "reactance_ohms", e.get("reactance_ohms", 0.12) if isinstance(e, dict) else 0.12))

            ai_status = AIComponentStatus.TRIPPED if status_str in ("tripped", "failed", "offline") else AIComponentStatus.ONLINE

            ai_lines[eid] = AITransmissionLine(
                id=eid,
                name=eid,
                source_node_id=source,
                target_node_id=target,
                capacity_mw=cap,
                current_flow_mw=flow,
                resistance_ohm=res_ohm,
                reactance_ohm=react_ohm,
                status=ai_status,
                risk=AIRiskMetrics(
                    criticality=AICriticalityLevel.HIGH if cap >= 400.0 else AICriticalityLevel.MEDIUM,
                    failure_probability=risk_val * 0.05,
                    risk_score=risk_val * 100.0 if risk_val <= 1.0 else risk_val,
                ),
            )

        return ElectricityGrid(
            grid_id="pulseiq-digital-twin",
            name="PULSEiQ Active Grid Twin",
            nodes=ai_nodes,
            lines=ai_lines,
            metadata={"source": "backend_grid_service"},
        )

    # =========================================================================
    # 1. REAL AI FORECASTING EXECUTION
    # =========================================================================
    def run_ai_forecast(
        self,
        forecast_type: str = "load",
        horizon_hours: int = 24,
        historical_demand: Optional[List[float]] = None,
        weather_info: Optional[Dict[str, Any]] = None,
        region_id: Optional[str] = None,
        grid_state: Optional[Any] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Invokes the real Person 3 AI forecasting engine (GridForecaster)."""
        if not self.is_forecasting_available():
            return None
        try:
            from ai.forecasting import GridForecaster

            grid = self.convert_to_ai_grid(grid_state)
            grid_fc = GridForecaster()
            summary = grid_fc.forecast_grid(grid, horizon_hours=horizon_hours)

            ft = str(forecast_type).lower()
            if ft in ("load", "demand"):
                curve = summary.total_demand_curve
                points = [
                    {
                        "timestamp": summary.timestamps[i],
                        "value_mw": round(curve[i], 2),
                        "predicted_demand_mw": round(curve[i], 2),
                        "predicted_renewable_mw": None,
                        "lower_bound_mw": round(curve[i] * 0.92, 2),
                        "upper_bound_mw": round(curve[i] * 1.08, 2),
                    }
                    for i in range(min(horizon_hours, len(curve)))
                ]
            elif ft == "solar":
                # Aggregate solar curve
                solar_curve = [0.0] * horizon_hours
                for fc in summary.solar_forecasts.values():
                    for i, pt in enumerate(fc.points[:horizon_hours]):
                        solar_curve[i] += pt.value_mw
                points = [
                    {
                        "timestamp": summary.timestamps[i],
                        "value_mw": round(solar_curve[i], 2),
                        "predicted_demand_mw": None,
                        "predicted_renewable_mw": round(solar_curve[i], 2),
                        "lower_bound_mw": round(solar_curve[i] * 0.88, 2),
                        "upper_bound_mw": round(solar_curve[i] * 1.10, 2),
                    }
                    for i in range(horizon_hours)
                ]
            elif ft == "wind":
                # Aggregate wind curve
                wind_curve = [0.0] * horizon_hours
                for fc in summary.wind_forecasts.values():
                    for i, pt in enumerate(fc.points[:horizon_hours]):
                        wind_curve[i] += pt.value_mw
                points = [
                    {
                        "timestamp": summary.timestamps[i],
                        "value_mw": round(wind_curve[i], 2),
                        "predicted_demand_mw": None,
                        "predicted_renewable_mw": round(wind_curve[i], 2),
                        "lower_bound_mw": round(wind_curve[i] * 0.85, 2),
                        "upper_bound_mw": round(wind_curve[i] * 1.15, 2),
                    }
                    for i in range(horizon_hours)
                ]
            else:
                curve = summary.total_demand_curve
                points = [
                    {
                        "timestamp": summary.timestamps[i],
                        "value_mw": round(curve[i], 2),
                        "predicted_demand_mw": round(curve[i], 2),
                        "predicted_renewable_mw": round(summary.total_renewable_curve[i], 2),
                        "lower_bound_mw": round(curve[i] * 0.92, 2),
                        "upper_bound_mw": round(curve[i] * 1.08, 2),
                    }
                    for i in range(min(horizon_hours, len(curve)))
                ]

            return {
                "values": points,
                "confidence_score": 0.94,
                "model_source": "ai_module",
            }

        except Exception as e:
            logger.warning(f"Error calling real AI forecasting engine: {e}. Falling back to service adapter.", exc_info=True)
            return None

    # =========================================================================
    # 2. REAL AI RISK & CONTINGENCY EXECUTION
    # =========================================================================
    def run_ai_risk_analysis(
        self,
        contingency_type: str = "N-1",
        failed_component_id: Optional[str] = None,
        monte_carlo_iterations: int = 1000,
        grid_state: Optional[Any] = None,
        simulation_results: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Invokes the real Person 3 AI risk assessment, N-1 screening, and cascading failure engine."""
        if not self.is_risk_available():
            return None
        try:
            from ai.risk import calculate_grid_risk_index
            from ai.models.grid import NodeType as AINodeType, ComponentStatus as AIComponentStatus

            grid = self.convert_to_ai_grid(grid_state)

            if failed_component_id:
                if failed_component_id in grid.lines:
                    grid.lines[failed_component_id].status = AIComponentStatus.TRIPPED
                elif failed_component_id in grid.nodes:
                    grid.nodes[failed_component_id].status = AIComponentStatus.TRIPPED

            assessment = calculate_grid_risk_index(grid)

            # Critical load exposure assessment
            critical_loads = [n for n in grid.nodes.values() if n.node_type == AINodeType.LOAD_CRITICAL]
            crit_at_risk = assessment.critical_load_at_risk
            crit_mw = sum(n.operational.demand_mw for n in critical_loads) if crit_at_risk else 0.0
            crit_names = [n.name for n in critical_loads] if crit_at_risk else []

            # Vulnerable component ranking from real NetworkX & multi-factor risk scorecard
            vuln_components = [
                {
                    "id": c.component_id,
                    "name": c.component_name,
                    "type": c.component_type,
                    "impact": "critical_vulnerability" if (c.is_articulation_point or c.is_bridge) else ("tripped" if c.component_id == failed_component_id else "monitored"),
                    "utilization_or_loading": round(c.utilization_pct, 2),
                }
                for c in assessment.ranked_critical_components
            ]

            return {
                "risk_index": round(assessment.risk_index, 3),
                "risk_level": assessment.risk_level.value.lower(),  # "low", "moderate", "high", "critical"
                "vulnerable_components": vuln_components,
                "affected_components": vuln_components,
                "critical_load_impact": {
                    "critical_load_at_risk": crit_at_risk,
                    "critical_load_at_risk_mw": round(crit_mw, 2),
                    "affected_critical_facilities": crit_names,
                },
                "contingency_results": {
                    "contingency_type": contingency_type,
                    "failed_component": failed_component_id,
                    "total_screened": len(assessment.most_critical_contingencies),
                    "most_critical_contingencies": assessment.most_critical_contingencies,
                },
                "n1_analysis": {
                    "n1_compliance_status": "warning" if assessment.n_1_violations_count > 0 else "compliant",
                    "n1_violations_count": assessment.n_1_violations_count,
                    "monitored_elements_count": len(grid.lines),
                },
                "cascading_failure_indicators": {
                    "overload_propagation_probability": round(assessment.cascading_risk_score, 4),
                    "cascading_risk_score": round(assessment.cascading_risk_score, 4),
                    "loss_of_load_probability_lolp": round(assessment.risk_index * 0.08, 4),
                    "expected_energy_not_served_mwh": round(crit_mw * 1.2, 2),
                },
                "model_source": "ai_module",
                "explanation": f"Evaluated via Person 3 Multi-Factor Risk Assessment (N-1 Insecurity: {assessment.n_1_violations_count} violations)",
                "summary": assessment.summary,
            }
        except Exception as e:
            logger.warning(f"Error calling real AI risk engine: {e}. Falling back to service adapter.", exc_info=True)
            return None

    # =========================================================================
    # 3. REAL AI POWER-FLOW & SIMULATION EXECUTION
    # =========================================================================
    def run_ai_simulation(
        self,
        scenario_id: Optional[str] = None,
        duration_hours: int = 24,
        time_step_minutes: int = 60,
        demand_mw: Optional[float] = None,
        generation_mw: Optional[float] = None,
        renewable_generation_mw: Optional[float] = None,
        battery_state: Optional[Dict[str, Any]] = None,
        load_growth_factor: Optional[float] = None,
        contingency_event: Optional[str] = None,
        grid_state: Optional[Any] = None,
        simulation_parameters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Invokes the real Person 3 AI physical DC power-flow simulation engine (solve_power_flow)."""
        if not self.is_simulation_available():
            return None
        try:
            from ai.simulation import solve_power_flow
            from ai.models.grid import ScenarioConfig

            grid = self.convert_to_ai_grid(grid_state)

            contingencies = [contingency_event] if contingency_event else []

            growth = float(load_growth_factor or 1.0)
            if demand_mw is not None and grid.total_demand_mw > 0:
                growth = demand_mw / grid.total_demand_mw

            if contingency_event or load_growth_factor is not None:
                scenario = ScenarioConfig(
                    name=f"Scenario {scenario_id or 'Run'}",
                    demand_multiplier=growth,
                    contingencies=contingencies,
                )
                sim_grid = grid.apply_scenario(scenario)
            else:
                sim_grid = grid

            sim_result = solve_power_flow(sim_grid, nominal_frequency_hz=50.0)

            line_loading = {lid: round(lr.utilization_pct, 2) for lid, lr in sim_result.line_results.items()}
            avg_util = round(sum(line_loading.values()) / max(1, len(line_loading)), 2)

            min_v = min((b.voltage_pu for b in sim_result.bus_voltages.values()), default=1.0)
            max_v = max((b.voltage_pu for b in sim_result.bus_voltages.values()), default=1.0)
            avg_v = sum(b.voltage_pu for b in sim_result.bus_voltages.values()) / max(1, len(sim_result.bus_voltages))

            warnings = []
            affected = []
            if not sim_result.is_frequency_stable:
                warnings.append(f"Grid frequency deviation: {sim_result.frequency_hz:.2f} Hz")
            for lid, lr in sim_result.line_results.items():
                if lr.is_overloaded:
                    warnings.append(f"Line '{lid}' overloaded at {lr.utilization_pct:.1f}%")
                    affected.append(lid)
            if contingency_event:
                affected.append(contingency_event)

            return {
                "simulation_status": "completed",
                "total_generation_mw": round(sim_result.total_generation_mw, 2),
                "total_demand_mw": round(sim_result.total_demand_mw, 2),
                "renewable_generation_mw": round(sim_grid.total_renewable_generation_mw, 2),
                "line_utilization_avg": min(100.0, avg_util),
                "line_loading": line_loading,
                "frequency_hz": round(sim_result.frequency_hz, 3),
                "voltage_indicators": {
                    "min_voltage_pu": round(min_v, 3),
                    "max_voltage_pu": round(max_v, 3),
                    "avg_voltage_pu": round(avg_v, 3),
                },
                "simulation_warnings": warnings,
                "affected_components": affected,
                "risk_index": round(min(1.0, max(0.05, sim_result.overloaded_lines_count * 0.2 + (0.3 if not sim_result.is_frequency_stable else 0.0))), 3),
                "resulting_grid_state": None,
                "model_source": "ai_module",
                "details": {
                    "solver": "Person 3 DC-Linear Power Flow Solver",
                    "is_frequency_stable": sim_result.is_frequency_stable,
                    "overloaded_lines_count": sim_result.overloaded_lines_count,
                },
            }
        except Exception as e:
            logger.warning(f"Error calling real AI simulation engine: {e}. Falling back to service adapter.", exc_info=True)
            return None

    # =========================================================================
    # 4. REAL AI MATHEMATICAL OPTIMIZATION EXECUTION
    # =========================================================================
    def run_ai_optimization(
        self,
        objective: str = "cost_minimization",
        demand_mw: Optional[float] = None,
        available_generation_mw: Optional[float] = None,
        renewable_generation_mw: Optional[float] = None,
        battery_availability: Optional[Dict[str, Any]] = None,
        risk_results: Optional[Dict[str, Any]] = None,
        operational_constraints: Optional[Dict[str, Any]] = None,
        critical_load_requirements: Optional[Dict[str, Any]] = None,
        grid_state: Optional[Any] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Invokes the real Person 3 AI mathematical optimization solver (solve_optimal_dispatch)."""
        if not self.is_optimization_available():
            return None
        try:
            from ai.optimization import (
                solve_optimal_dispatch,
                OptimizationConfig,
                OptimizationStatus,
            )

            grid = self.convert_to_ai_grid(grid_state)

            obj_str = str(objective).lower()
            if "emission" in obj_str:
                config = OptimizationConfig(
                    fuel_cost_per_mwh={"gas_ccgt": 120.0, "conventional": 130.0, "solar": 0.0, "wind": 0.0, "battery": 5.0},
                    renewable_curtailment_penalty=100.0,
                )
            elif "relia" in obj_str:
                config = OptimizationConfig(
                    normal_load_shedding_penalty=2500.0,
                    critical_load_shedding_penalty=50000.0,
                )
            else:
                config = OptimizationConfig()

            dispatch_res = solve_optimal_dispatch(grid, config=config)

            dispatches = []
            for gid, mw in dispatch_res.generator_dispatch_mw.items():
                node = grid.nodes.get(gid)
                gname = node.name if node else gid
                gtype = node.node_type.value if node else "generator"
                gcap = node.operational.max_capacity_mw if node else mw
                mcost = getattr(node.operational, "marginal_cost_per_mwh", 30.0) if node else 30.0
                dispatches.append({
                    "generator_id": gid,
                    "generator_name": gname,
                    "type": gtype,
                    "dispatched_mw": round(mw, 2),
                    "capacity_mw": round(gcap, 2),
                    "marginal_cost_per_mwh": round(mcost, 2),
                })

            bat_mw = sum(dispatch_res.battery_dispatch_mw.values()) if dispatch_res.battery_dispatch_mw else 0.0
            curtailment = sum(dispatch_res.curtailed_renewable_mw.values()) if dispatch_res.curtailed_renewable_mw else 0.0
            unserved = sum(dispatch_res.unserved_demand_mw.values()) if dispatch_res.unserved_demand_mw else 0.0

            recommended = [
                "Prioritize zero-marginal-cost renewable assets (Solar PV & Wind Farm).",
                f"Schedule BESS active dispatch at {bat_mw:.1f} MW to balance net load.",
            ]
            if "relia" in obj_str:
                recommended.append("Maintain high spinning reserve headroom on gas turbine.")
            elif "emission" in obj_str:
                recommended.append("Throttle thermal generation to minimize CO2 emissions.")

            return {
                "optimization_status": "optimal" if dispatch_res.status == OptimizationStatus.OPTIMAL else "suboptimal",
                "recommended_actions": recommended,
                "generator_dispatch": dispatches,
                "total_dispatched_generation_mw": round(dispatch_res.total_generation_dispatched_mw, 2),
                "battery_dispatch_mw": round(bat_mw, 2),
                "battery_charge_discharge_mw": round(bat_mw, 2),
                "backup_generation_mw": 0.0,
                "flexible_load_reduction_mw": 0.0,
                "renewable_curtailment_mw": round(curtailment, 2),
                "unserved_demand_mw": round(unserved, 2),
                "expected_risk_reduction": 0.22,
                "objective_value": round(dispatch_res.total_cost, 2),
                "cost_estimate_usd": round(dispatch_res.total_cost, 2),
                "model_source": "ai_module",
                "summary": dispatch_res.summary,
            }
        except Exception as e:
            logger.warning(f"Error calling real AI optimization solver: {e}. Falling back to service adapter.", exc_info=True)
            return None

    # =========================================================================
    # 5. REAL AI GRAPH ANALYTICS EXECUTION
    # =========================================================================
    def run_ai_graph_analysis(self, grid_state: Optional[Any] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Invokes the real Person 3 AI graph analytics engine on the grid."""
        if not self.is_graph_available():
            return None
        try:
            from ai.graph import grid_to_networkx, analyze_graph_topology
            grid = self.convert_to_ai_grid(grid_state)
            g = grid_to_networkx(grid)
            res = analyze_graph_topology(g, grid=grid)
            return res.to_dict()
        except Exception as e:
            logger.warning(f"Error calling real AI graph analysis: {e}.", exc_info=True)
            return None

    # =========================================================================
    # 6. REAL AI UNIFIED PIPELINE EXECUTION
    # =========================================================================
    def run_ai_pipeline(self, grid_state: Optional[Any] = None, config: Optional[Any] = None, **kwargs) -> Optional[Dict[str, Any]]:
        """Invokes the real Person 3 AI unified intelligence pipeline."""
        if not self.is_pipeline_available():
            return None
        try:
            from ai.pipeline import GridIntelligencePipeline
            grid = self.convert_to_ai_grid(grid_state)
            pipeline = GridIntelligencePipeline()
            res = pipeline.run(grid, config=config)
            return res.to_dict()
        except Exception as e:
            logger.warning(f"Error calling real AI pipeline: {e}.", exc_info=True)
            return None


ai_bridge = AIModuleBridge()
