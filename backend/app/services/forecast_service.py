import math
from datetime import datetime, timedelta, timezone
from backend.app.schemas.forecast import (
    ForecastType,
    ForecastDataPoint,
    ForecastRequest,
    ForecastResponse,
)
from backend.app.core.ai_bridge import ai_bridge


class ForecastService:
    """Service providing time-series forecasting for load demand, solar, and wind generation.
    Interfaces directly with Person 3's Scikit-learn/XGBoost/PyTorch AI models when present,
    providing deterministic fallback generation when the AI module is offline.
    """

    def generate_forecast(self, request: ForecastRequest) -> ForecastResponse:
        """Generates hourly forecast time-series for the specified horizon and target."""
        # 1. Attempt delegation to Person 3's AI Forecasting module
        if ai_bridge.is_forecasting_available():
            ai_result = ai_bridge.run_ai_forecast(
                forecast_type=request.forecast_type.value,
                horizon_hours=request.horizon_hours,
                historical_demand=request.historical_demand_mw,
                weather_info=request.weather_info,
                region_id=request.region_id,
            )
            if ai_result and isinstance(ai_result, dict) and "values" in ai_result:
                points = [
                    ForecastDataPoint(
                        timestamp=p.get("timestamp", datetime.now(timezone.utc).isoformat()),
                        predicted_demand_mw=p.get("predicted_demand_mw", p.get("value_mw")),
                        predicted_renewable_mw=p.get("predicted_renewable_mw"),
                        value_mw=p.get("value_mw", 0.0),
                        lower_bound_mw=p.get("lower_bound_mw"),
                        upper_bound_mw=p.get("upper_bound_mw"),
                    )
                    for p in ai_result["values"]
                ]
                vals = [p.value_mw for p in points]
                return ForecastResponse(
                    forecast_type=request.forecast_type,
                    horizon_hours=request.horizon_hours,
                    values=points,
                    peak_mw=round(max(vals), 2) if vals else 0.0,
                    min_mw=round(min(vals), 2) if vals else 0.0,
                    average_mw=round(sum(vals) / len(vals), 2) if vals else 0.0,
                    confidence_score=ai_result.get("confidence_score", 0.94),
                    model_source="ai_module",
                    generated_at=datetime.now(timezone.utc).isoformat(),
                )

        # 2. High-fidelity analytical fallback
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        data_points = []
        horizon = request.horizon_hours
        target = request.forecast_type

        for step in range(horizon):
            point_time = now + timedelta(hours=step)
            hour_of_day = point_time.hour

            if target == ForecastType.LOAD:
                base = 380.0
                daily_variation = 70.0 * math.sin(math.pi * (hour_of_day - 6) / 12) if 6 <= hour_of_day <= 22 else -40.0
                noise = 8.0 * math.sin(step * 0.7)
                value = round(base + daily_variation + noise, 2)
                lower = round(value * 0.94, 2)
                upper = round(value * 1.06, 2)
                dem_mw = value
                ren_mw = None

            elif target == ForecastType.SOLAR:
                if 6 <= hour_of_day <= 18:
                    peak_solar = 160.0
                    solar_factor = math.sin(math.pi * (hour_of_day - 6) / 12)
                    value = round(peak_solar * (solar_factor ** 1.5), 2)
                    lower = round(value * 0.88, 2)
                    upper = round(value * 1.08, 2)
                else:
                    value = 0.0
                    lower = 0.0
                    upper = 0.0
                dem_mw = None
                ren_mw = value

            elif target == ForecastType.WIND:
                base_wind = 85.0
                wind_variation = 35.0 * math.sin(math.pi * (hour_of_day - 12) / 12)
                gust_noise = 12.0 * math.cos(step * 0.5)
                value = round(max(15.0, min(145.0, base_wind + wind_variation + gust_noise)), 2)
                lower = round(max(0.0, value * 0.85), 2)
                upper = round(value * 1.15, 2)
                dem_mw = None
                ren_mw = value

            else:
                value = 100.0
                lower = 90.0
                upper = 110.0
                dem_mw = value
                ren_mw = None

            data_points.append(
                ForecastDataPoint(
                    timestamp=point_time.isoformat(),
                    predicted_demand_mw=dem_mw,
                    predicted_renewable_mw=ren_mw,
                    value_mw=value,
                    lower_bound_mw=lower,
                    upper_bound_mw=upper,
                )
            )

        values_list = [p.value_mw for p in data_points]
        peak_mw = round(max(values_list), 2)
        min_mw = round(min(values_list), 2)
        avg_mw = round(sum(values_list) / len(values_list), 2)

        return ForecastResponse(
            forecast_type=target,
            horizon_hours=horizon,
            values=data_points,
            peak_mw=peak_mw,
            min_mw=min_mw,
            average_mw=avg_mw,
            confidence_score=0.91,
            model_source="service_fallback",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )


forecast_service = ForecastService()
