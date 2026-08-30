"""
PULSEiQ - Real Electricity Dataset Training & Feature Engineering Pipeline.
Trains a production-grade machine learning model (HistGradientBoostingRegressor)
on real historical multi-year electricity demand telemetry from LD2011_2014.txt.
"""

import os
import sys
import time
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Set threads to prevent OpenBLAS / OMP memory allocation errors on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"


def parse_and_resample_electricity_data(raw_filepath: str, output_csv: str = None) -> pd.DataFrame:
    """
    Memory-safe streaming parser for LD2011_2014.txt (678 MB).
    Reads line by line, aggregates the 370 consumers (kW -> MW),
    and resamples from 15-minute intervals to hourly average active demand.
    """
    print(f"[*] Starting memory-safe stream parsing of {raw_filepath}...")
    start_time = time.time()

    hourly_sums = {}
    hourly_counts = {}

    total_lines = 0
    with open(raw_filepath, "r", encoding="utf-8", errors="ignore") as f:
        header_line = f.readline().strip().replace('"', "").split(";")
        num_clients = len(header_line) - 1
        print(f"[*] Identified {num_clients} electricity client meter columns.")

        for line in f:
            total_lines += 1
            if not line.strip():
                continue

            parts = line.strip().split(";")
            if len(parts) < 2:
                continue

            # First item is timestamp: "YYYY-MM-DD HH:MM:SS"
            ts_str = parts[0].replace('"', "").strip()
            if len(ts_str) < 13:
                continue

            # Extract hourly bucket key: "YYYY-MM-DD HH:00:00"
            hour_bucket = ts_str[:13] + ":00:00"

            # Parse client kW values and compute total active power
            total_kw = 0.0
            for val_str in parts[1:]:
                # Decimal separator is comma in European format: "123,45" -> 123.45
                clean_str = val_str.replace(",", ".").strip()
                if clean_str and clean_str != "0":
                    try:
                        total_kw += float(clean_str)
                    except ValueError:
                        pass

            # Convert total kW to MW
            total_mw = total_kw / 1000.0

            hourly_sums[hour_bucket] = hourly_sums.get(hour_bucket, 0.0) + total_mw
            hourly_counts[hour_bucket] = hourly_counts.get(hour_bucket, 0) + 1

            if total_lines % 25000 == 0:
                print(f"    Processed {total_lines:,} raw 15-minute records ({time.time() - start_time:.1f}s)...")

    print(f"[*] Finished streaming {total_lines:,} raw records in {time.time() - start_time:.1f}s.")
    print(f"[*] Aggregating into {len(hourly_sums):,} hourly time-series intervals...")

    records = []
    for dt_str, sum_mw in hourly_sums.items():
        count = hourly_counts[dt_str]
        avg_mw = sum_mw / count if count > 0 else 0.0
        records.append({"timestamp": dt_str, "demand_mw": avg_mw})

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Filter out initial ramp-up period (early 2011 when meters were inactive / 0)
    # The stable active grid monitoring period spans 2012-01-01 onwards
    df_clean = df[df["timestamp"] >= "2012-01-01 00:00:00"].copy().reset_index(drop=True)
    print(f"[*] Filtered stable period (2012-2014): {len(df_clean):,} hourly records.")

    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_clean.to_csv(output_csv, index=False)
        print(f"[*] Saved clean processed hourly dataset to {output_csv}")

    return df_clean


def engineer_features(df: pd.DataFrame) -> tuple:
    """
    Constructs non-leaking time-series lag, cyclical, and moving-window features.
    """
    data = df.copy()
    dt = data["timestamp"].dt

    # 1. Calendar & Cyclical Harmonic Features
    data["hour"] = dt.hour
    data["hour_sin"] = np.sin(2 * np.pi * data["hour"] / 24.0)
    data["hour_cos"] = np.cos(2 * np.pi * data["hour"] / 24.0)

    data["day_of_week"] = dt.dayofweek
    data["dow_sin"] = np.sin(2 * np.pi * data["day_of_week"] / 7.0)
    data["dow_cos"] = np.cos(2 * np.pi * data["day_of_week"] / 7.0)

    data["day_of_month"] = dt.day
    data["month"] = dt.month
    data["month_sin"] = np.sin(2 * np.pi * data["month"] / 12.0)
    data["month_cos"] = np.cos(2 * np.pi * data["month"] / 12.0)

    data["is_weekend"] = (data["day_of_week"] >= 5).astype(int)

    # 2. Autoregressive Lags (Strictly non-leaking past information)
    data["lag_1"] = data["demand_mw"].shift(1)
    data["lag_2"] = data["demand_mw"].shift(2)
    data["lag_3"] = data["demand_mw"].shift(3)
    data["lag_24"] = data["demand_mw"].shift(24)    # Same hour previous day
    data["lag_48"] = data["demand_mw"].shift(48)    # Same hour 2 days ago
    data["lag_168"] = data["demand_mw"].shift(168)  # Same hour previous week

    # 3. Rolling Window Statistics (Using past lags to prevent data leakage)
    data["rolling_mean_6"] = data["demand_mw"].shift(1).rolling(6, min_periods=1).mean()
    data["rolling_mean_24"] = data["demand_mw"].shift(1).rolling(24, min_periods=1).mean()
    data["rolling_std_24"] = data["demand_mw"].shift(1).rolling(24, min_periods=1).std().fillna(0.0)
    data["rolling_min_24"] = data["demand_mw"].shift(1).rolling(24, min_periods=1).min()
    data["rolling_max_24"] = data["demand_mw"].shift(1).rolling(24, min_periods=1).max()

    # 4. Interaction Ratios
    data["daily_ratio"] = data["lag_1"] / np.maximum(data["rolling_mean_24"], 0.1)

    feature_cols = [
        "hour", "hour_sin", "hour_cos",
        "day_of_week", "dow_sin", "dow_cos",
        "day_of_month", "month", "month_sin", "month_cos",
        "is_weekend",
        "lag_1", "lag_2", "lag_3", "lag_24", "lag_48", "lag_168",
        "rolling_mean_6", "rolling_mean_24", "rolling_std_24",
        "rolling_min_24", "rolling_max_24", "daily_ratio",
    ]

    # Drop warm-up rows containing initial NaN lags (first 168 hours / 1 week)
    data_clean = data.dropna(subset=feature_cols).reset_index(drop=True)
    return data_clean, feature_cols


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """Calculate comprehensive time-series forecast evaluation metrics."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))

    # Safe MAPE avoiding division by zero
    non_zero = y_true > 0.01
    if np.any(non_zero):
        mape = float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100.0)
    else:
        mape = 0.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "mape_pct": round(mape, 3),
        "r2": round(r2, 4),
    }


def train_and_evaluate():
    """Main execution pipeline."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_path = os.path.join(base_dir, "data", "raw", "LD2011_2014.txt")
    processed_path = os.path.join(base_dir, "data", "processed", "hourly_electricity_demand.csv")
    artifacts_dir = os.path.join(base_dir, "ai", "forecasting", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    if not os.path.exists(raw_path):
        print(f"[!] Error: Raw dataset not found at {raw_path}")
        sys.exit(1)

    # 1. Parse and Resample Data
    t0 = time.time()
    df_hourly = parse_and_resample_electricity_data(raw_path, output_csv=processed_path)

    # 2. Feature Engineering
    df_feat, feature_cols = engineer_features(df_hourly)
    print(f"[*] Total engineered samples: {len(df_feat):,} with {len(feature_cols)} features.")

    # 3. Chronological Train / Validation / Test Split (70% / 15% / 15%)
    n_total = len(df_feat)
    n_train = int(n_total * 0.70)
    n_val = int(n_total * 0.15)
    n_test = n_total - n_train - n_val

    train_df = df_feat.iloc[:n_train].copy()
    val_df = df_feat.iloc[n_train:n_train + n_val].copy()
    test_df = df_feat.iloc[n_train + n_val:].copy()

    X_train, y_train = train_df[feature_cols], train_df["demand_mw"]
    X_val, y_val = val_df[feature_cols], val_df["demand_mw"]
    X_test, y_test = test_df[feature_cols], test_df["demand_mw"]

    print("\n" + "=" * 60)
    print("CHRONOLOGICAL SPLIT DETAILS:")
    print(f"  Train set:      {len(train_df):,} rows ({train_df['timestamp'].min()} to {train_df['timestamp'].max()})")
    print(f"  Validation set: {len(val_df):,} rows ({val_df['timestamp'].min()} to {val_df['timestamp'].max()})")
    print(f"  Test set:       {len(test_df):,} rows ({test_df['timestamp'].min()} to {test_df['timestamp'].max()})")
    print("=" * 60)

    # 4. Previous-Day Persistence Baseline (y_pred = lag_24)
    y_test_baseline = test_df["lag_24"].values
    baseline_metrics = calculate_metrics(y_test.values, y_test_baseline)

    print("\n" + "=" * 60)
    print("BASELINE (24h Persistence) TEST METRICS:")
    print(f"  MAE:      {baseline_metrics['mae']:.2f} MW")
    print(f"  RMSE:     {baseline_metrics['rmse']:.2f} MW")
    print(f"  MAPE:     {baseline_metrics['mape_pct']:.2f}%")
    print(f"  R2 Score: {baseline_metrics['r2']:.4f}")
    print("=" * 60)

    # 5. Train HistGradientBoostingRegressor
    print("\n[*] Training HistGradientBoostingRegressor on real electricity data...")
    train_start = time.time()

    model = HistGradientBoostingRegressor(
        max_iter=180,
        learning_rate=0.07,
        max_depth=7,
        min_samples_leaf=20,
        l2_regularization=0.1,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=15,
    )
    model.fit(X_train, y_train)
    train_duration = time.time() - train_start
    print(f"[*] Training completed in {train_duration:.2f} seconds.")

    # 6. Evaluation
    val_preds = model.predict(X_val)
    val_metrics = calculate_metrics(y_val.values, val_preds)

    test_preds = model.predict(X_test)
    test_metrics = calculate_metrics(y_test.values, test_preds)

    print("\n" + "=" * 60)
    print("ML MODEL (HistGradientBoostingRegressor) METRICS:")
    print(f"  Validation MAE:  {val_metrics['mae']:.2f} MW | RMSE: {val_metrics['rmse']:.2f} MW | MAPE: {val_metrics['mape_pct']:.2f}% | R2: {val_metrics['r2']:.4f}")
    print(f"  Test MAE:        {test_metrics['mae']:.2f} MW | RMSE: {test_metrics['rmse']:.2f} MW | MAPE: {test_metrics['mape_pct']:.2f}% | R2: {test_metrics['r2']:.4f}")
    print("=" * 60)

    improvement_pct = ((baseline_metrics["mae"] - test_metrics["mae"]) / baseline_metrics["mae"]) * 100.0
    print(f"[*] ML Model Outperforms Previous-Day Baseline by {improvement_pct:.2f}% reduction in MAE!")

    # 7. Uncertainty Error Residuals for Confidence Intervals
    residuals = y_val.values - val_preds
    error_q10 = float(np.percentile(residuals, 10))
    error_q90 = float(np.percentile(residuals, 90))
    error_std = float(np.std(residuals))

    # 8. Save Trained Model and Metadata
    model_save_path = os.path.join(artifacts_dir, "demand_model.joblib")
    joblib.dump(model, model_save_path, compress=3)
    print(f"[*] Saved trained model to {model_save_path} (Size: {os.path.getsize(model_save_path) / 1024:.1f} KB)")

    metadata = {
        "model_name": "HistGradientBoostingRegressor",
        "dataset_name": "UCI Electricity Load Diagrams (LD2011_2014)",
        "trained_at": datetime.now().isoformat(),
        "training_duration_seconds": round(train_duration, 2),
        "total_hourly_records": n_total,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "feature_columns": feature_cols,
        "baseline_metrics": baseline_metrics,
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
        "improvement_over_baseline_mae_pct": round(improvement_pct, 2),
        "error_residual_std": round(error_std, 4),
        "error_q10": round(error_q10, 4),
        "error_q90": round(error_q90, 4),
        "mean_demand_mw": round(float(y_train.mean()), 2),
        "max_demand_mw": round(float(y_train.max()), 2),
        "min_demand_mw": round(float(y_train.min()), 2),
    }

    metadata_path = os.path.join(artifacts_dir, "model_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[*] Saved training metadata to {metadata_path}")

    total_time = time.time() - t0
    print(f"\n[SUCCESS] End-to-end dataset processing & ML training finished in {total_time:.1f}s.")
    return metadata


if __name__ == "__main__":
    train_and_evaluate()
