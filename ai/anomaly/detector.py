"""
PULSEiQ - Demand Anomaly Detection Module.
Leverages Scikit-Learn IsolationForest to detect irregular electricity load spikes,
unexpected drop-offs, and multi-scale temporal anomalies across time-series demand data.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from ai.anomaly.models import AnomalyDetectionResult, AnomalyPoint, AnomalyStatus
from ai.forecasting.generators import generate_synthetic_load_dataset
from ai.models.grid import NodeType

logger = logging.getLogger(__name__)

ANOMALY_FEATURE_NAMES = ["demand", "hour", "day_of_week", "lag_1", "lag_24", "lag_168"]


def extract_anomaly_features(
    df: pd.DataFrame,
    target_col: str = "demand",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extracts demand anomaly features [demand, hour, day_of_week, lag_1, lag_24, lag_168]
    from a DataFrame, dynamically computing lag columns if not already present.
    """
    df_feat = df.copy()

    # Normalize demand column name
    if target_col not in df_feat.columns:
        if "target_demand_mw" in df_feat.columns:
            target_col = "target_demand_mw"
        elif "value_mw" in df_feat.columns:
            target_col = "value_mw"
        else:
            raise KeyError(f"Target column '{target_col}' not found in DataFrame columns: {list(df_feat.columns)}")

    df_feat["demand"] = df_feat[target_col].astype(float)

    # Extract temporal features from timestamp or existing columns
    if "hour" not in df_feat.columns or "day_of_week" not in df_feat.columns:
        if "timestamp" in df_feat.columns:
            dts = pd.to_datetime(df_feat["timestamp"])
            df_feat["hour"] = dts.dt.hour
            df_feat["day_of_week"] = dts.dt.dayofweek
        else:
            df_feat["hour"] = [i % 24 for i in range(len(df_feat))]
            df_feat["day_of_week"] = [(i // 24) % 7 for i in range(len(df_feat))]

    # Compute autoregressive lag features if missing
    if "lag_1" not in df_feat.columns:
        df_feat["lag_1"] = df_feat["demand"].shift(1).bfill()
    if "lag_24" not in df_feat.columns:
        df_feat["lag_24"] = df_feat["demand"].shift(24).bfill()
    if "lag_168" not in df_feat.columns:
        df_feat["lag_168"] = df_feat["demand"].shift(168).bfill()

    # Fill any remaining NaNs safely
    for col in ANOMALY_FEATURE_NAMES:
        if col in df_feat.columns:
            df_feat[col] = df_feat[col].bfill().ffill().fillna(0.0)

    X = df_feat[ANOMALY_FEATURE_NAMES].copy()
    return X, df_feat


class DemandAnomalyDetector:
    """
    Scikit-learn IsolationForest anomaly detector for electric load time-series telemetry.
    Identifies demand surges, structural drops, and atypical usage profiles.
    """

    def __init__(
        self,
        contamination: float = 0.03,
        n_estimators: int = 100,
        random_state: int = 42,
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model_name = "IsolationForest"

        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.is_fitted = False

    def fit(
        self,
        training_data: Optional[Union[pd.DataFrame, Sequence[float]]] = None,
        target_col: str = "demand",
    ) -> DemandAnomalyDetector:
        """
        Trains the IsolationForest model on historical demand telemetry.
        If no training data is passed, initializes baseline training from standard grid telemetry.
        """
        if training_data is None:
            df_train = generate_synthetic_load_dataset(
                node_id="baseline_normal_load",
                node_type=NodeType.LOAD_NORMAL,
                base_demand_mw=50.0,
                hours=672,  # 4 weeks history
                seed=self.random_state,
            )
            target_col = "target_demand_mw"
        elif isinstance(training_data, pd.DataFrame):
            df_train = training_data.copy()
        else:
            # List or 1D array of floats
            df_train = pd.DataFrame({"demand": list(training_data)})
            target_col = "demand"

        X_train, _ = extract_anomaly_features(df_train, target_col=target_col)
        self.model.fit(X_train)
        self.is_fitted = True
        return self

    def predict(
        self,
        data: Union[pd.DataFrame, Sequence[float]],
        target_col: str = "demand",
        timestamps: Optional[List[str]] = None,
    ) -> AnomalyDetectionResult:
        """
        Evaluates incoming demand telemetry observations and assigns anomaly classifications.
        Produces timestamp, observed demand, anomaly flag, numeric anomaly score, and status.
        """
        if not self.is_fitted:
            self.fit()

        if isinstance(data, pd.DataFrame):
            df_eval = data.copy()
        else:
            df_eval = pd.DataFrame({"demand": list(data)})
            target_col = "demand"

        if timestamps is not None and "timestamp" not in df_eval.columns:
            df_eval["timestamp"] = timestamps[:len(df_eval)]

        X_eval, df_processed = extract_anomaly_features(df_eval, target_col=target_col)

        # IsolationForest predict: 1 for normal (inliers), -1 for anomaly (outliers)
        raw_preds = self.model.predict(X_eval)
        # Decision function: lower/negative values indicate anomalous observations
        raw_scores = self.model.decision_function(X_eval)

        points: List[AnomalyPoint] = []
        anomaly_count = 0

        for i in range(len(df_processed)):
            row = df_processed.iloc[i]
            is_anomaly = bool(raw_preds[i] == -1)
            status_str = AnomalyStatus.ANOMALY.value if is_anomaly else AnomalyStatus.NORMAL.value
            score_val = float(round(raw_scores[i], 4))
            observed_mw = float(round(row["demand"], 3))

            ts_str = str(row["timestamp"]) if "timestamp" in row else datetime.now(timezone.utc).isoformat()

            if is_anomaly:
                anomaly_count += 1

            points.append(
                AnomalyPoint(
                    timestamp=ts_str,
                    observed_demand=observed_mw,
                    anomaly_flag=is_anomaly,
                    anomaly_score=score_val,
                    status=status_str,
                )
            )

        total_obs = len(points)
        rate_pct = round((anomaly_count / max(total_obs, 1)) * 100.0, 2)

        return AnomalyDetectionResult(
            total_observations=total_obs,
            anomalies_detected=anomaly_count,
            anomaly_rate_pct=rate_pct,
            points=points,
            model_name=self.model_name,
            contamination=self.contamination,
        )

    def detect_anomalies(
        self,
        data: Union[pd.DataFrame, Sequence[float]],
        target_col: str = "demand",
    ) -> AnomalyDetectionResult:
        """Alias for predict()."""
        return self.predict(data, target_col=target_col)
