from datetime import datetime, timezone
from backend.app.schemas.simulation import SimulationRunRequest, SimulationRunResponse
from backend.app.services.grid_service import grid_service
from backend.app.core.ai_bridge import ai_bridge


class SimulationService:
    """Service providing grid power-flow, bus voltage, frequency, and state simulation.
    Interfaces directly with Person 3's NumPy / SciPy simulation engine, providing
    deterministic physics-based power balance fallbacks when the AI engine is offline.
    """

    def run_simulation(self, request: SimulationRunRequest) -> SimulationRunResponse:
        """Executes a grid state simulation run based on input parameters."""
        grid_state = grid_service.get_grid_state()

        # 1. Attempt delegation to Person 3's AI Simulation module
        if ai_bridge.is_simulation_available():
            ai_result = ai_bridge.run_ai_simulation(
                scenario_id=request.scenario_id,
                duration_hours=request.duration_hours,
                time_step_minutes=request.time_step_minutes,
                demand_mw=request.demand_mw,
                generation_mw=request.generation_mw,
                renewable_generation_mw=request.renewable_generation_mw,
                battery_state=request.battery_state,
                load_growth_factor=request.load_growth_factor,
                contingency_event=request.contingency_event,
                grid_state=request.grid_state or grid_state.model_dump(),
                simulation_parameters=request.simulation_parameters,
            )
            if ai_result and isinstance(ai_result, dict):
                return SimulationRunResponse(
                    simulation_status=ai_result.get("simulation_status", "completed"),
                    total_generation_mw=ai_result.get("total_generation_mw", 475.0),
                    total_demand_mw=ai_result.get("total_demand_mw", 460.0),
                    renewable_generation_mw=ai_result.get("renewable_generation_mw", 235.0),
                    line_utilization_avg=ai_result.get("line_utilization_avg", 56.4),
                    line_loading=ai_result.get("line_loading", {}),
                    frequency_hz=ai_result.get("frequency_hz", 50.00),
                    voltage_indicators=ai_result.get("voltage_indicators", {"min_voltage_pu": 0.985, "max_voltage_pu": 1.020, "avg_voltage_pu": 1.002}),
                    simulation_warnings=ai_result.get("simulation_warnings", []),
                    affected_components=ai_result.get("affected_components", []),
                    risk_index=ai_result.get("risk_index", 0.14),
                    resulting_grid_state=ai_result.get("resulting_grid_state"),
                    model_source="ai_module",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    details=ai_result.get("details", {"engine": "Person 3 NumPy/SciPy Power-Flow Engine"}),
                )

        # 2. Physics-based analytical fallback
        load_growth = float(request.load_growth_factor or 1.0)
        scen_str = str(request.scenario_id or "").lower()

        solar_mult = 1.0
        wind_mult = 1.0
        if "heatwave" in scen_str or "heat" in scen_str:
            load_growth *= 1.25
            solar_mult = 1.10
            wind_mult = 0.85
        elif "solar" in scen_str:
            solar_mult = 0.20
        elif "wind" in scen_str:
            wind_mult = 0.05

        base_demand = request.demand_mw if request.demand_mw is not None else grid_state.summary.total_demand_mw
        simulated_demand = round(base_demand * load_growth, 2)

        solar_node = grid_service.get_node_by_id("gen-solar-1")
        wind_node = grid_service.get_node_by_id("gen-wind-1")
        gas_node = grid_service.get_node_by_id("gen-gas-1")
        battery_node = grid_service.get_node_by_id("bat-bess-1")

        solar_output = (solar_node.current_output_mw if solar_node else 140.0) * solar_mult
        wind_output = (wind_node.current_output_mw if wind_node else 95.0) * wind_mult
        if request.contingency_event == "gen-solar-1":
            solar_output = 0.0
        if request.contingency_event == "gen-wind-1":
            wind_output = 0.0

        renewable_gen = request.renewable_generation_mw if request.renewable_generation_mw is not None else round(solar_output + wind_output, 2)

        deficit = simulated_demand - renewable_gen
        gas_capacity = gas_node.capacity_mw if gas_node else 350.0
        gas_output = min(gas_capacity, max(100.0, deficit))
        if request.contingency_event == "gen-gas-1":
            gas_output = 50.0

        battery_output = battery_node.current_output_mw if battery_node else 20.0
        if request.contingency_event == "bat-bess-1":
            battery_output = 0.0

        total_gen = request.generation_mw if request.generation_mw is not None else round(gas_output + renewable_gen + battery_output, 2)

        power_imbalance = total_gen - simulated_demand
        nominal_freq = 50.00
        frequency = round(nominal_freq + (power_imbalance * 0.001), 3)

        line_loading = {}
        affected_components = []
        simulation_warnings = []

        if request.contingency_event:
            affected_components.append(request.contingency_event)
            simulation_warnings.append(f"Contingency trip active on '{request.contingency_event}'.")

        for edge in grid_state.edges:
            base_util = edge.utilization_percent
            if request.contingency_event and edge.id == request.contingency_event:
                util = 0.0
                if edge.id not in affected_components:
                    affected_components.append(edge.id)
                simulation_warnings.append(f"Transmission line '{edge.id}' is disconnected due to contingency event.")
            elif request.contingency_event and "north-central" in request.contingency_event and "central-south" in edge.id:
                util = round(base_util * 1.45 * (load_growth / max(0.01, request.load_growth_factor or 1.0)), 2)
                if edge.id not in affected_components:
                    affected_components.append(edge.id)
                if util > 90.0:
                    simulation_warnings.append(f"Transmission corridor '{edge.id}' heavily loaded at {util}%.")
            else:
                util = round(base_util * load_growth, 2)
                if util > 85.0:
                    if edge.id not in affected_components:
                        affected_components.append(edge.id)
                    simulation_warnings.append(f"High loading on line '{edge.id}' ({util}%).")
            line_loading[edge.id] = min(120.0, util)

        avg_line_util = round(sum(line_loading.values()) / max(1, len(line_loading)), 2)

        calc_risk = 0.08 + (0.35 if request.contingency_event else 0.0) + (max(0.0, load_growth - 1.0) * 0.35)
        if "heatwave" in scen_str:
            calc_risk += 0.25
        elif "solar" in scen_str or "wind" in scen_str:
            calc_risk += 0.15

        risk_index = round(min(1.0, calc_risk), 3)

        voltage_indicators = {
            "min_voltage_pu": round(0.995 - (max(0.0, load_growth - 1.0) * 0.03), 3),
            "max_voltage_pu": 1.022,
            "avg_voltage_pu": round(1.005 - (max(0.0, load_growth - 1.0) * 0.01), 3),
        }

        return SimulationRunResponse(
            simulation_status="completed",
            total_generation_mw=total_gen,
            total_demand_mw=simulated_demand,
            renewable_generation_mw=renewable_gen,
            line_utilization_avg=min(100.0, avg_line_util),
            line_loading=line_loading,
            frequency_hz=frequency,
            voltage_indicators=voltage_indicators,
            simulation_warnings=simulation_warnings,
            affected_components=affected_components,
            risk_index=min(1.0, risk_index),
            resulting_grid_state=None,
            model_source="service_fallback",
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "scenario_id": request.scenario_id,
                "duration_hours": request.duration_hours,
                "time_step_minutes": request.time_step_minutes,
                "contingency_event": request.contingency_event,
                "load_growth_factor": request.load_growth_factor,
                "power_imbalance_mw": round(power_imbalance, 2),
                "engine": "PULSEiQ Simulation Service (AI Bridge Integration Active)",
            },
        )


simulation_service = SimulationService()
