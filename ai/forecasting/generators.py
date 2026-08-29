"""
PULSEiQ - Synthetic Time-Series Generators & Feature Engineering Pipelines.
Generates realistic historical and future datasets for demand, solar, and wind generation
without requiring external raw files.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from ai.models.grid import NodeType


def generate_synthetic_timestamps(hours: int = 168, start_time: Optional[datetime] = None) -> List[datetime]:
    """Generate a sequence of hourly UTC datetimes."""
    if start_time is None:
        start_time = datetime(2026, 8, 1, 0, 0, 0, tzinfo=timezone.utc)
    return [start_time + timedelta(hours=i) for i in range(hours)]


def generate_synthetic_weather(hours: int = 168, start_time: Optional[datetime] = None, seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic ambient temperature, solar irradiance (GHI), and wind speed profiles.
    """
    rng = np.random.RandomState(seed)
    timestamps = generate_synthetic_timestamps(hours, start_time)

    records = []
    for i, dt in enumerate(timestamps):
        hour = dt.hour
        day_of_year = dt.timetuple().tm_yday

        # 1. Temperature: seasonal base (22C) + diurnal oscillation (peak at 3pm / 15:00) + noise
        diurnal_temp = 6.0 * np.sin((hour - 9) * np.pi / 12.0)
        ambient_temp = 22.0 + diurnal_temp + rng.normal(0, 1.2)

        # 2. Solar Irradiance (W/m^2): Bell curve between 06:00 and 19:00, 0 at night
        if 6 <= hour <= 19:
            solar_angle = max(0.0, float(np.sin((hour - 6) * np.pi / 13.0)))
            cloud_factor = float(np.clip(1.0 - rng.exponential(0.12), 0.1, 1.0))
            solar_irradiance = 950.0 * (solar_angle ** 1.3) * cloud_factor + rng.normal(0, 15)
            solar_irradiance = max(0.0, solar_irradiance)
        else:
            solar_irradiance = 0.0

        # 3. Wind Speed (m/s): Diurnal gust factor + Weibull distributed background wind
        base_wind = rng.weibull(2.1) * 7.5
        diurnal_wind = 1.5 * np.sin((hour - 14) * np.pi / 12.0)
        wind_speed = np.clip(base_wind + diurnal_wind + rng.normal(0, 0.6), 0.0, 30.0)

        records.append({
            "timestamp": dt.isoformat(),
            "hour": hour,
            "day_of_week": dt.weekday(),
            "is_weekend": int(dt.weekday() >= 5),
            "temperature_c": round(ambient_temp, 2),
            "solar_irradiance_wm2": round(solar_irradiance, 2),
            "wind_speed_mps": round(wind_speed, 2),
        })

    return pd.DataFrame(records)


def generate_synthetic_load_dataset(
    node_id: str,
    node_type: NodeType,
    base_demand_mw: float,
    hours: int = 168,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic historical hourly demand records for training/testing.
    """
    weather_df = generate_synthetic_weather(hours=hours, seed=seed)
    rng = np.random.RandomState(seed + 10)

    demands = []
    for _, row in weather_df.iterrows():
        hour = row["hour"]
        is_weekend = row["is_weekend"]
        temp = row["temperature_c"]

        # Base diurnal shape
        if node_type == NodeType.LOAD_CRITICAL:
            # Critical loads (hospitals, data centers) have very flat, high-reliability baseload demand
            hourly_factor = 0.92 + 0.12 * np.sin((hour - 8) * np.pi / 12.0) ** 2
            weekend_factor = 0.98 if is_weekend else 1.0
            temp_sensitivity = 0.005 * max(0.0, temp - 24.0)  # Moderate HVAC cooling
            noise = rng.normal(0, 0.02)
        elif node_type == NodeType.LOAD_NORMAL:
            # Residential/commercial: Dual peaks (morning 8am, evening 7pm) and weekend shifts
            morning_peak = np.exp(-((hour - 8) ** 2) / 8.0) * 0.25
            evening_peak = np.exp(-((hour - 19) ** 2) / 10.0) * 0.40
            base_shape = 0.60 + morning_peak + evening_peak
            weekend_factor = 0.88 if is_weekend else 1.0
            temp_sensitivity = 0.02 * max(0.0, temp - 22.0) + 0.015 * max(0.0, 16.0 - temp)
            noise = rng.normal(0, 0.04)
            hourly_factor = base_shape
        else:
            hourly_factor = 1.0
            weekend_factor = 1.0
            temp_sensitivity = 0.0
            noise = rng.normal(0, 0.02)

        demand = base_demand_mw * hourly_factor * weekend_factor * (1.0 + temp_sensitivity) * (1.0 + noise)
        demands.append(max(0.1, round(demand, 3)))

    weather_df["target_demand_mw"] = demands
    weather_df["node_id"] = node_id
    return weather_df


def generate_synthetic_solar_dataset(
    node_id: str,
    capacity_mw: float,
    hours: int = 168,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic solar generation dataset based on irradiance and panel thermal degradation.
    """
    weather_df = generate_synthetic_weather(hours=hours, seed=seed)
    rng = np.random.RandomState(seed + 20)

    gen_values = []
    for _, row in weather_df.iterrows():
        irr = row["solar_irradiance_wm2"]
        temp = row["temperature_c"]

        if irr <= 5.0:
            gen_values.append(0.0)
            continue

        # Standard solar PV efficiency: standard 1000 W/m^2 rating with -0.4%/°C temperature coefficient
        temp_loss = 1.0 - 0.004 * max(0.0, temp - 25.0)
        inverter_eff = 0.97
        power = (irr / 1000.0) * capacity_mw * temp_loss * inverter_eff
        power += rng.normal(0, 0.01 * capacity_mw)
        power = float(np.clip(power, 0.0, capacity_mw))
        gen_values.append(round(power, 3))

    weather_df["target_generation_mw"] = gen_values
    weather_df["node_id"] = node_id
    return weather_df


def generate_synthetic_wind_dataset(
    node_id: str,
    capacity_mw: float,
    hours: int = 168,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generates realistic wind generation dataset based on non-linear turbine power curves.
    Cut-in: 3 m/s, Rated: 12 m/s, Cut-out: 25 m/s.
    """
    weather_df = generate_synthetic_weather(hours=hours, seed=seed)
    rng = np.random.RandomState(seed + 30)

    gen_values = []
    for _, row in weather_df.iterrows():
        v = row["wind_speed_mps"]

        if v < 3.0 or v >= 25.0:
            power = 0.0
        elif 3.0 <= v < 12.0:
            # Cubic aerodynamic curve
            power = capacity_mw * ((v - 3.0) / (12.0 - 3.0)) ** 3
        else:  # 12.0 <= v < 25.0
            power = capacity_mw

        power += rng.normal(0, 0.02 * capacity_mw)
        power = float(np.clip(power, 0.0, capacity_mw))
        gen_values.append(round(power, 3))

    weather_df["target_generation_mw"] = gen_values
    weather_df["node_id"] = node_id
    return weather_df


def extract_forecasting_features(df: pd.DataFrame, target_col: str = "target_demand_mw") -> Tuple[pd.DataFrame, pd.Series]:
    """
    Extracts time-series lag and cyclical features for ML training.
    """
    data = df.copy()

    # Cyclical hour features
    data["hour_sin"] = np.sin(2 * np.pi * data["hour"] / 24.0)
    data["hour_cos"] = np.cos(2 * np.pi * data["hour"] / 24.0)
    data["dow_sin"] = np.sin(2 * np.pi * data["day_of_week"] / 7.0)
    data["dow_cos"] = np.cos(2 * np.pi * data["day_of_week"] / 7.0)

    # Lags & rolling windows
    if target_col in data.columns:
        data["lag_1"] = data[target_col].shift(1).bfill()
        data["lag_2"] = data[target_col].shift(2).bfill()
        data["lag_24"] = data[target_col].shift(24).bfill()
        data["rolling_mean_6"] = data[target_col].rolling(6, min_periods=1).mean()
        data["rolling_mean_24"] = data[target_col].rolling(24, min_periods=1).mean()
    else:
        data["lag_1"] = 0.0
        data["lag_2"] = 0.0
        data["lag_24"] = 0.0
        data["rolling_mean_6"] = 0.0
        data["rolling_mean_24"] = 0.0

    feature_cols = [
        "hour", "hour_sin", "hour_cos", "day_of_week", "dow_sin", "dow_cos", "is_weekend",
        "temperature_c", "solar_irradiance_wm2", "wind_speed_mps",
        "lag_1", "lag_2", "lag_24", "rolling_mean_6", "rolling_mean_24",
    ]

    X = data[feature_cols]
    y = data[target_col] if target_col in data.columns else pd.Series(np.zeros(len(data)))
    return X, y
