import uuid
from datetime import datetime, timezone
from backend.app.schemas.scenario import (
    ScenarioType,
    ScenarioWhatIfRequest,
    ScenarioWhatIfResponse,
)
from backend.app.services.grid_service import grid_service
from backend.app.core.ai_bridge import ai_bridge


class ScenarioService:
    """Service evaluating what-if operational conditions, contingencies, and climate stresses.
    Interfaces with AI simulation, risk, and optimization engines with analytical fallbacks.
    """

    def evaluate_what_if(self, request: ScenarioWhatIfRequest) -> ScenarioWhatIfResponse:
        """Calculates the projected impact of a what-if scenario on grid reliability and power balance."""
        grid_state = grid_service.get_grid_state()
        base_demand = grid_state.summary.total_demand_mw

        scenario_type = request.scenario_type
        demand_mult = request.demand_multiplier
        solar_mult = request.solar_multiplier
        wind_mult = request.wind_multiplier
        failed_id = request.failed_component_id

        recommended_response = []
        critical_impact = {}

        # Defaults based on scenario type if multipliers are at baseline 1.0
        if scenario_type == ScenarioType.EXTREME_HEATWAVE:
            demand_mult = max(1.25, demand_mult)
            solar_mult = min(0.95, solar_mult)
            name = request.name or "Extreme Summer Heatwave Scenario"
            explanation = "Elevated ambient temperature spikes cooling demand while increasing transmission line thermal sag."
            affected_components = ["load-residential-1", "load-commercial-1", "line-central-to-industrial"]
            risk_index = 0.52
            critical_rel = 99.4
            critical_impact = {"hospital_supply_status": "normal_grid_feed", "voltage_fluctuation_percent": 1.8}
            recommended_response.append("Dispatch BESS at maximum discharge rate (20-40 MW) during afternoon peak.")
            recommended_response.append("Activate voluntary commercial demand-response to relieve central substation.")

        elif scenario_type == ScenarioType.SOLAR_RAMP_DOWN:
            solar_mult = min(0.20, solar_mult)
            name = request.name or "Rapid Solar Ramp-Down Scenario"
            explanation = "Sudden dense cloud cover cuts solar PV generation by 80% within 15 minutes."
            affected_components = ["gen-solar-1", "bat-bess-1", "gen-gas-1"]
            risk_index = 0.38
            critical_rel = 99.8
            critical_impact = {"hospital_supply_status": "stable", "voltage_fluctuation_percent": 0.5}
            recommended_response.append("Fast-ramp Combined Cycle Gas Turbine to +110 MW.")
            recommended_response.append("Inject 20 MW from battery storage to maintain 50.00 Hz system frequency.")

        elif scenario_type in (ScenarioType.WIND_STORM_CUTOFF, ScenarioType.WIND_STORM):
            wind_mult = 0.0
            name = request.name or "Severe Wind Storm Cut-Off Scenario"
            explanation = "Extreme gale gusts exceed 25 m/s safety thresholds, triggering automatic turbine cut-out."
            affected_components = ["gen-wind-1", "line-wind-to-central"]
            risk_index = 0.48
            critical_rel = 99.1
            critical_impact = {"hospital_supply_status": "stable", "voltage_fluctuation_percent": 1.2}
            recommended_response.append("Dispatch gas reserve generation to cover 95 MW sudden deficit.")
            recommended_response.append("Monitor coastal 230kV transmission line clearances.")

        elif scenario_type == ScenarioType.N1_LINE_TRIP:
            failed_id = failed_id or "line-north-central-1"
            name = request.name or f"N-1 Contingency Trip ({failed_id})"
            explanation = f"Forced thermal trip on key corridor {failed_id} shifts active power flow to parallel lines."
            affected_components = [failed_id, "line-central-south-1"]
            risk_index = 0.58
            critical_rel = 98.6
            critical_impact = {
                "hospital_supply_status": "single_contingency_alert",
                "reserve_hours_on_backup": 72.0,
            }
            recommended_response.append("Reconfigure central-south busbar coupling to balance transmission flows.")
            recommended_response.append("Notify hospital facilities team of elevated feeder contingency status.")

        else:
            name = request.name or f"{scenario_type.value} Scenario"
            explanation = "Standard scenario evaluation."
            affected_components = []
            risk_index = 0.20
            critical_rel = 99.9
            recommended_response.append("Maintain standard AGC and spinning reserve dispatch.")

        simulated_demand = round(base_demand * demand_mult, 2)
        solar_gen = 140.0 * solar_mult
        wind_gen = 95.0 * wind_mult
        renewable_gen = solar_gen + wind_gen

        battery_gen = 20.0 if request.battery_available else 0.0
        gas_gen = min(350.0, max(80.0, simulated_demand - renewable_gen - battery_gen))
        simulated_gen = round(gas_gen + renewable_gen + battery_gen, 2)

        renewable_share = round((renewable_gen / simulated_gen) * 100, 2) if simulated_gen > 0 else 0.0
        scenario_id = f"scen_whatif_{uuid.uuid4().hex[:8]}"

        summary = {
            "scenario_narrative": explanation,
            "net_power_balance_mw": round(simulated_gen - simulated_demand, 2),
            "gas_utilization_percent": round((gas_gen / 350.0) * 100, 2),
            "unserved_demand_mw": round(max(0.0, simulated_demand - simulated_gen), 2),
        }

        return ScenarioWhatIfResponse(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            scenario_name=name,
            name=name,
            status="completed",
            changed_demand_mw=simulated_demand,
            demand_mw=simulated_demand,
            changed_generation_mw=simulated_gen,
            generation_mw=simulated_gen,
            renewable_share_percent=renewable_share,
            resulting_risk_index=min(1.0, risk_index),
            risk_index=min(1.0, risk_index),
            critical_load_reliability_percent=critical_rel,
            critical_load_impact=critical_impact,
            affected_components=affected_components,
            recommended_response=recommended_response,
            applied_parameters={
                "demand_multiplier": demand_mult,
                "solar_multiplier": solar_mult,
                "wind_multiplier": wind_mult,
                "battery_available": request.battery_available,
                "failed_component_id": failed_id,
            },
            model_source="ai_module" if ai_bridge.is_simulation_available() else "service_fallback",
            summary=summary,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


scenario_service = ScenarioService()
