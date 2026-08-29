from datetime import datetime, timezone
from backend.app.schemas.risk import (
    RiskLevel,
    AffectedComponent,
    RiskAnalysisRequest,
    RiskAnalysisResponse,
)
from backend.app.services.grid_service import grid_service


class RiskService:
    """Service providing grid security, contingency, and probabilistic risk evaluation.
    Provides a standardized contract abstraction for Person 3's Monte Carlo and
    cascading failure analysis modules.
    """

    def analyze_risk(self, request: RiskAnalysisRequest) -> RiskAnalysisResponse:
        """Evaluates contingency conditions and calculates grid risk metrics."""
        grid_state = grid_service.get_grid_state()
        failed_id = request.failed_component_id

        affected_components = []
        affected_load_mw = 0.0
        critical_load_at_risk = False
        critical_load_mw = 0.0

        if failed_id:
            # Analyze specific component outage
            if failed_id == "line-north-central-1":
                affected_components.append(
                    AffectedComponent(
                        id="line-central-south-1",
                        name="Central-South 115kV Intertie",
                        type="transmission_line",
                        impact="overloaded",
                        utilization_or_loading=92.5,
                    )
                )
                affected_components.append(
                    AffectedComponent(
                        id="load-industrial-1",
                        name="East Harbor Industrial Zone",
                        type="load",
                        impact="voltage_drop",
                        utilization_or_loading=85.0,
                    )
                )
                risk_index = 0.58
                risk_level = RiskLevel.HIGH
                affected_load_mw = 65.0
                cascade_prob = 0.34
                explanation = (
                    f"Outage of primary backbone {failed_id} redirects 340 MW onto parallel corridor line-central-south-1, "
                    f"increasing thermal utilization to 92.5% and causing voltage sag at East Harbor Industrial Zone."
                )

            elif failed_id == "line-south-to-hospital" or failed_id == "load-hospital-metro":
                critical_load_at_risk = True
                critical_load_mw = 45.0
                affected_load_mw = 45.0
                risk_index = 0.85
                risk_level = RiskLevel.CRITICAL
                affected_components.append(
                    AffectedComponent(
                        id="load-hospital-metro",
                        name="Metro University Hospital & Trauma Center",
                        type="critical_load",
                        impact="isolated_feeder",
                        utilization_or_loading=100.0,
                    )
                )
                cascade_prob = 0.15
                explanation = (
                    f"Outage of critical feeder {failed_id} isolates Metro University Hospital. "
                    f"Emergency backup generators must engage within 10 seconds to avoid loss of life-support infrastructure."
                )

            else:
                risk_index = 0.32
                risk_level = RiskLevel.MODERATE
                cascade_prob = 0.12
                explanation = f"Contingency trip on component {failed_id} successfully absorbed by N-1 spinning reserves."

        else:
            # Baseline or extreme weather evaluation
            if request.contingency_type == "extreme_weather":
                risk_index = 0.62
                risk_level = RiskLevel.HIGH
                affected_load_mw = 80.0
                cascade_prob = 0.40
                explanation = "Severe storm conditions elevate transmission line trip probability across all coastal assets."
            else:
                risk_index = grid_state.summary.grid_risk_index
                risk_level = RiskLevel.LOW
                cascade_prob = 0.05
                explanation = "Nominal operating state: all N-1 security criteria satisfied with adequate spinning reserve."

        cascading_indicators = {
            "overload_propagation_probability": cascade_prob,
            "max_cascade_depth": 2 if risk_index > 0.5 else 0,
            "loss_of_load_probability_lolp": round(risk_index * 0.08, 4),
            "expected_energy_not_served_mwh": round(affected_load_mw * 1.5, 2),
            "overloaded_lines_count": sum(1 for c in affected_components if c.type == "transmission_line"),
        }

        summary = {
            "contingency_type": request.contingency_type,
            "iterations_evaluated": request.monte_carlo_iterations,
            "system_reserve_margin_percent": 18.5,
            "n1_compliance_status": "warning" if risk_index > 0.5 else "compliant",
        }

        return RiskAnalysisResponse(
            risk_index=round(risk_index, 3),
            risk_level=risk_level,
            affected_components=affected_components,
            affected_load_mw=round(affected_load_mw, 2),
            critical_load_at_risk=critical_load_at_risk,
            critical_load_at_risk_mw=round(critical_load_mw, 2),
            cascading_failure_indicators=cascading_indicators,
            explanation=explanation,
            summary=summary,
            analyzed_at=datetime.now(timezone.utc).isoformat(),
        )


risk_service = RiskService()
