"""
Unit tests for PULSEiQ Unified AI/ML Prediction & Risk Pipeline (Step 4).
"""

import copy
import json
import pytest

from ai.models.grid import ComponentStatus, ElectricityGrid, GridNode, NodeType, OperationalData, RiskMetrics, TransmissionLine
from ai.models.mock_grid import create_mock_grid
from ai.pipeline import (
    GridAIPipeline,
    GridIntelligencePipeline,
    GridIntelligenceResult,
    PipelineConfig,
    PipelineInput,
    PipelineValidationError,
)


def test_pipeline_end_to_end_success():
    """Verify that GridIntelligencePipeline runs all modular engines and returns a typed result."""
    grid = create_mock_grid()
    pipeline = GridIntelligencePipeline()

    result = pipeline.run(grid)

    assert isinstance(result, GridIntelligenceResult)
    assert result.status == "SUCCESS"

    # 1. Forecast section assertions
    fc = result.forecast
    assert fc.horizon_hours == 24
    assert len(fc.load_forecast_mw) == 24
    assert len(fc.solar_forecast_mw) == 24
    assert len(fc.wind_forecast_mw) == 24
    assert len(fc.net_load_forecast_mw) == 24
    assert fc.total_forecasted_demand_mwh > 0.0
    assert fc.total_forecasted_renewable_mwh > 0.0
    assert fc.peak_demand_mw > 0.0
    assert len(fc.timestamps) == 24
    assert len(fc.time_series_points) == 24

    # 2. Risk section assertions
    risk = result.risk
    assert 0.0 <= risk.score <= 1.0
    assert risk.level in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert "transmission_loading" in risk.factors
    assert "critical_load_exposure" in risk.factors
    assert risk.n_1_violations_count >= 0
    assert isinstance(risk.critical_load_at_risk, bool)
    assert len(risk.most_critical_contingencies) <= 5
    assert risk.cascading_report is not None

    # 3. Topology section assertions
    topo = result.topology
    assert topo.node_count == 12
    assert topo.edge_count == 12
    assert topo.is_connected is True
    assert len(topo.critical_nodes) > 0
    assert "sub_trans_main" in topo.articulation_points
    assert len(topo.bridges) > 0

    # 4. Simulation section assertions
    sim = result.simulation
    assert sim.power_flow_converged is True
    assert sim.total_generation_mw > 100.0
    assert sim.total_demand_mw > 100.0
    assert 59.0 <= sim.frequency_hz <= 61.0
    assert sim.is_frequency_stable is True

    # 5. Ranked components assertions
    assert len(result.ranked_critical_components) <= 5
    for rank_idx, comp in enumerate(result.ranked_critical_components, start=1):
        assert comp["overall_criticality_rank"] == rank_idx
        assert "risk_score" in comp
        assert "centrality_score" in comp

    # 6. Metadata assertions
    meta = result.metadata
    assert meta.grid_id == grid.grid_id
    assert meta.grid_name == grid.name
    assert meta.pipeline_version == "1.0.0"
    assert meta.execution_time_ms > 0.0

    # 7. Test serialization
    dict_payload = result.to_dict()
    assert isinstance(dict_payload, dict)
    assert json.dumps(dict_payload) is not None


def test_pipeline_alias_and_custom_config():
    """Verify GridAIPipeline alias and custom configuration options."""
    grid = create_mock_grid()
    pipeline = GridAIPipeline()

    cfg = PipelineConfig(
        forecast_horizon_hours=12,
        include_monte_carlo=True,
        monte_carlo_trials=25,
        n_1_top_k=3,
        ranked_components_top_k=3,
    )

    result = pipeline.run(grid, config=cfg)

    assert result.forecast.horizon_hours == 12
    assert len(result.forecast.load_forecast_mw) == 12
    assert len(result.risk.most_critical_contingencies) <= 3
    assert len(result.ranked_critical_components) == 3
    # Monte Carlo results populated
    assert result.simulation.loss_of_load_probability is not None
    assert result.simulation.expected_unserved_energy_mwh is not None


def test_pipeline_telemetry_integration():
    """Verify that live telemetry correctly updates grid operational values."""
    grid = create_mock_grid()
    pipeline = GridIntelligencePipeline()

    telemetry_payload = {
        "nodes": {
            "load_residential_north": {"demand_mw": 45.0},
        },
        "lines": {
            "line_submain_to_subnorth": {"current_flow_mw": 60.0},
        },
    }

    result = pipeline.run(grid, telemetry=telemetry_payload)
    assert result.status == "SUCCESS"
    assert result.simulation.total_demand_mw >= 128.5


def test_validation_rejects_none_and_empty():
    """Verify that pipeline rejects None and empty inputs with clear errors."""
    pipeline = GridIntelligencePipeline()

    with pytest.raises(PipelineValidationError, match="Expected ElectricityGrid or PipelineInput"):
        pipeline.run(None)

    empty_grid = ElectricityGrid(grid_id="empty_grid", name="Empty")
    with pytest.raises(PipelineValidationError, match="contains no nodes"):
        pipeline.run(empty_grid)


def test_validation_rejects_invalid_numbers():
    """Verify that negative node demand or line capacity raises PipelineValidationError."""
    pipeline = GridIntelligencePipeline()

    invalid_grid = create_mock_grid()
    invalid_grid.nodes["load_hospital_main"].operational.demand_mw = -10.0

    with pytest.raises(PipelineValidationError, match="negative value for 'demand_mw'"):
        pipeline.run(invalid_grid)

    invalid_line_grid = create_mock_grid()
    invalid_line_grid.lines["line_submain_to_subnorth"].capacity_mw = -50.0

    with pytest.raises(PipelineValidationError, match="Capacity must be > 0"):
        pipeline.run(invalid_line_grid)


def test_validation_rejects_invalid_config():
    """Verify configuration boundary validation."""
    grid = create_mock_grid()
    pipeline = GridIntelligencePipeline()

    with pytest.raises(PipelineValidationError, match="forecast_horizon_hours must be a positive integer"):
        pipeline.run(grid, config=PipelineConfig(forecast_horizon_hours=0))

    with pytest.raises(PipelineValidationError, match="cannot exceed 168 hours"):
        pipeline.run(grid, config=PipelineConfig(forecast_horizon_hours=200))

    with pytest.raises(PipelineValidationError, match="monte_carlo_trials must be at least 1"):
        pipeline.run(grid, config=PipelineConfig(monte_carlo_trials=0))


def test_validation_rejects_malformed_telemetry():
    """Verify that malformed telemetry referencing unknown components is rejected."""
    grid = create_mock_grid()
    pipeline = GridIntelligencePipeline()

    bad_telemetry = {
        "nodes": {
            "unknown_ghost_bus": {"demand_mw": 50.0},
        }
    }

    with pytest.raises(PipelineValidationError, match="unknown node ID 'unknown_ghost_bus'"):
        pipeline.run(grid, telemetry=bad_telemetry)
