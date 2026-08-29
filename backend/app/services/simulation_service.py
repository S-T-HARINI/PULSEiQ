from datetime import datetime, timezone
from backend.app.schemas.simulation import SimulationRunRequest, SimulationRunResponse
from backend.app.services.grid_service import grid_service


class SimulationService:
    """Service providing grid power-flow and state simulation capabilities.
    Designed with a clean abstraction layer to allow Person 3 to seamlessly
    swap in full AC/DC power-flow solvers or dynamic ODE simulation engines.
    """

    def run_simulation(self, request: SimulationRunRequest) -> SimulationRunResponse:
        """Executes a grid state simulation run based on input parameters."""
        grid_state = grid_service.get_grid_state()
        load_growth = request.load_growth_factor or 1.0

        # Compute dynamic response metrics
        base_demand = grid_state.summary.total_demand_mw
        simulated_demand = round(base_demand * load_growth, 2)

        # Solar and Wind base output
        solar_node = grid_service.get_node_by_id("gen-solar-1")
        wind_node = grid_service.get_node_by_id("gen-wind-1")
        gas_node = grid_service.get_node_by_id("gen-gas-1")
        battery_node = grid_service.get_node_by_id("bat-bess-1")

        solar_output = solar_node.current_output_mw if solar_node else 140.0
        wind_output = wind_node.current_output_mw if wind_node else 95.0
        renewable_gen = round(solar_output + wind_output, 2)

        # Gas turbine ramps to balance load
        deficit = simulated_demand - renewable_gen
        gas_capacity = gas_node.capacity_mw if gas_node else 350.0
        gas_output = min(gas_capacity, max(100.0, deficit))
        battery_output = battery_node.current_output_mw if battery_node else 20.0

        total_gen = round(gas_output + renewable_gen + battery_output, 2)

        # Frequency response based on power balance
        power_imbalance = total_gen - simulated_demand
        nominal_freq = 50.00
        frequency = round(nominal_freq + (power_imbalance * 0.001), 3)

        # Line loading calculations
        active_lines = len(grid_state.edges)
        line_utilizations = [edge.utilization_percent for edge in grid_state.edges]
        if request.contingency_event:
            # Contingency event creates stress on remaining lines
            avg_line_util = round(sum(line_utilizations) / active_lines * 1.18, 2)
            risk_index = 0.42
        else:
            avg_line_util = round(sum(line_utilizations) / active_lines, 2)
            risk_index = round(grid_state.summary.grid_risk_index + (max(0.0, load_growth - 1.0) * 0.25), 3)

        # Bus voltage indicators in per-unit (p.u.)
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
            frequency_hz=frequency,
            voltage_indicators=voltage_indicators,
            risk_index=min(1.0, risk_index),
            timestamp=datetime.now(timezone.utc).isoformat(),
            details={
                "scenario_id": request.scenario_id,
                "duration_hours": request.duration_hours,
                "time_step_minutes": request.time_step_minutes,
                "contingency_event": request.contingency_event,
                "load_growth_factor": request.load_growth_factor,
                "power_imbalance_mw": round(power_imbalance, 2),
                "engine": "PULSEiQ Simulation Service (Engine Hook Ready)",
            },
        )


simulation_service = SimulationService()
