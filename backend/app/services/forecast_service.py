import math
from datetime import datetime, timedelta, timezone
from backend.app.schemas.forecast import (
    ForecastType,
    ForecastDataPoint,
    ForecastRequest,
    ForecastResponse,
)


class ForecastService:
    """Service providing realistic time-series forecasting for electricity grid loads
    and renewable generation profiles. Provides a clean abstraction interface for
    Person 3's machine learning and statistical forecasting models.
    """

    def generate_forecast(self, request: ForecastRequest) -> ForecastResponse:
        """Generates hourly forecast time-series for the specified horizon and target."""
        now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
        data_points = []

        horizon = request.horizon_hours
        target = request.forecast_type

        # Base profiles and diurnal curve generation
        for step in range(horizon):
            point_time = now + timedelta(hours=step)
            hour_of_day = point_time.hour

            if target == ForecastType.LOAD:
                # Diurnal dual-peak load curve (morning and evening peaks)
                base = 380.0
                daily_variation = 70.0 * math.sin(math.pi * (hour_of_day - 6) / 12) if 6 <= hour_of_day <= 22 else -40.0
                noise = 8.0 * math.sin(step * 0.7)
                value = round(base + daily_variation + noise, 2)
                lower = round(value * 0.94, 2)
                upper = round(value * 1.06, 2)

            elif target == ForecastType.SOLAR:
                # Bell curve centered around noon (07:00 to 19:00)
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

            elif target == ForecastType.WIND:
                # Wind speed profile with coastal breeze peak in late afternoon
                base_wind = 85.0
                wind_variation = 35.0 * math.sin(math.pi * (hour_of_day - 12) / 12)
                gust_noise = 12.0 * math.cos(step * 0.5)
                value = round(max(15.0, min(145.0, base_wind + wind_variation + gust_noise)), 2)
                lower = round(max(0.0, value * 0.85), 2)
                upper = round(value * 1.15, 2)

            else:
                value = 100.0
                lower = 90.0
                upper = 110.0

            data_points.append(
                ForecastDataPoint(
                    timestamp=point_time.isoformat(),
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
            generated_at=datetime.now(timezone.utc).isoformat(),
        )


forecast_service = ForecastService()
