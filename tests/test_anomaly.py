"""
Unit tests for PULSEiQ Demand Anomaly Detection Module.
Tests IsolationForest-based anomaly detection on normal historical demand,
deliberate extreme demand spikes, anomalous observation flagging, and result structures.
"""

import numpy as np
import pandas as pd
import pytest

from ai.anomaly import (
    ANOMALY_FEATURE_NAMES,
    AnomalyDetectionResult,
    AnomalyPoint,
    AnomalyStatus,
    DemandAnomalyDetector,
    extract_anomaly_features,
)
from ai.forecasting.generators import generate_synthetic_load_dataset
from ai.models.grid import NodeType


def test_extract_anomaly_features():
    """Verify feature extraction extracts all required features [demand, hour, day_of_week, lag_1, lag_24, lag_168]."""
    df = generate_synthetic_load_dataset("node_test", NodeType.LOAD_NORMAL, base_demand_mw=40.0, hours=200, seed=42)
    X, df_processed = extract_anomaly_features(df, target_col="target_demand_mw")

    assert list(X.columns) == ANOMALY_FEATURE_NAMES
    assert len(X) == 200
    assert not X.isnull().values.any()
    assert "demand" in X.columns
    assert "lag_1" in X.columns
    assert "lag_24" in X.columns
    assert "lag_168" in X.columns


def test_normal_historical_demand_mostly_normal():
    """Verify normal historical demand is classified mostly as NORMAL."""
    df_normal = generate_synthetic_load_dataset(
        "node_normal",
        NodeType.LOAD_NORMAL,
        base_demand_mw=45.0,
        hours=336,
        seed=42,
    )

    detector = DemandAnomalyDetector(contamination=0.03, random_state=42)
    detector.fit(df_normal, target_col="target_demand_mw")
    result = detector.predict(df_normal, target_col="target_demand_mw")

    assert isinstance(result, AnomalyDetectionResult)
    assert result.total_observations == 336
    assert result.model_name == "IsolationForest"
    assert result.contamination == 0.03

    # Normal observations should remain mostly NORMAL (>95%)
    normal_points = [p for p in result.points if p.status == AnomalyStatus.NORMAL.value]
    normal_pct = (len(normal_points) / result.total_observations) * 100.0
    assert normal_pct >= 95.0, f"Expected at least 95% normal observations, got {normal_pct}%"


def test_deliberate_demand_spike_flagged_as_anomaly():
    """Verify a deliberately inserted massive demand spike (e.g. 5x base demand) is flagged as ANOMALY."""
    df_eval = generate_synthetic_load_dataset(
        "node_spike",
        NodeType.LOAD_NORMAL,
        base_demand_mw=40.0,
        hours=200,
        seed=42,
    )

    # Insert severe deliberate demand spike at index 150 (normal ~40MW -> 250MW spike)
    spike_idx = 150
    df_eval.loc[spike_idx, "target_demand_mw"] = 260.0

    detector = DemandAnomalyDetector(contamination=0.03, random_state=42)
    detector.fit()  # Fit on standard baseline normal telemetry
    result = detector.predict(df_eval, target_col="target_demand_mw")

    # Check the spiked point
    spike_point = result.points[spike_idx]
    assert spike_point.anomaly_flag is True, f"Spike at index {spike_idx} was not flagged as anomaly"
    assert spike_point.status == AnomalyStatus.ANOMALY.value
    assert spike_point.observed_demand == 260.0
    assert isinstance(spike_point.anomaly_score, float)
    assert spike_point.anomaly_score < 0.0, f"Expected negative anomaly decision score, got {spike_point.anomaly_score}"


def test_anomaly_point_structure_and_numeric_scores():
    """Verify output structure contains all required fields and numeric anomaly scores."""
    df = generate_synthetic_load_dataset(
        "node_struct",
        NodeType.LOAD_NORMAL,
        base_demand_mw=50.0,
        hours=48,
        seed=42,
    )

    detector = DemandAnomalyDetector(random_state=42)
    result = detector.predict(df, target_col="target_demand_mw")

    assert len(result.points) == 48
    for pt in result.points:
        assert isinstance(pt.timestamp, str) and len(pt.timestamp) > 0
        assert isinstance(pt.observed_demand, float) and pt.observed_demand > 0.0
        assert isinstance(pt.anomaly_flag, bool)
        assert isinstance(pt.anomaly_score, float)
        assert pt.status in (AnomalyStatus.NORMAL.value, AnomalyStatus.ANOMALY.value)

    res_dict = result.to_dict()
    assert "total_observations" in res_dict
    assert "anomalies_detected" in res_dict
    assert "anomaly_rate_pct" in res_dict
    assert "points" in res_dict
    assert len(res_dict["points"]) == 48
