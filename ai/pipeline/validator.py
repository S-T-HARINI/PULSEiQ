"""
PULSEiQ - Pipeline Input Validation and Sanity Checking.
Validates grid models, configuration parameters, and live telemetry feeds
before pipeline execution.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from ai.models.grid import ElectricityGrid, GridNode, TransmissionLine
from ai.pipeline.models import PipelineConfig, PipelineInput


class PipelineValidationError(ValueError):
    """Exception raised when input data or configuration fails validation."""
    def __init__(self, message: str, field_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.field_name = field_name
        self.details = details or {}


def validate_pipeline_input(pipeline_input: PipelineInput) -> None:
    """
    Validates a PipelineInput object including its grid topology, configuration, and telemetry.

    Raises:
        PipelineValidationError: If any validation rule is violated.
    """
    if pipeline_input is None:
        raise PipelineValidationError("PipelineInput cannot be None.", field_name="pipeline_input")

    if pipeline_input.grid is None:
        raise PipelineValidationError("ElectricityGrid inside PipelineInput cannot be None.", field_name="grid")

    validate_grid_model(pipeline_input.grid)

    if pipeline_input.config is not None:
        validate_pipeline_config(pipeline_input.config, pipeline_input.grid)

    if pipeline_input.telemetry is not None:
        validate_telemetry(pipeline_input.telemetry, pipeline_input.grid)


def validate_grid_model(grid: ElectricityGrid) -> None:
    """
    Validates the integrity of an ElectricityGrid instance.

    Raises:
        PipelineValidationError: If nodes, lines, or electrical parameters are invalid.
    """
    if not isinstance(grid, ElectricityGrid):
        raise PipelineValidationError(
            f"Expected instance of ElectricityGrid, got {type(grid).__name__}.",
            field_name="grid",
        )

    if not grid.grid_id or not isinstance(grid.grid_id, str) or not grid.grid_id.strip():
        raise PipelineValidationError("ElectricityGrid must have a non-empty string 'grid_id'.", field_name="grid_id")

    if not grid.nodes or len(grid.nodes) == 0:
        raise PipelineValidationError("ElectricityGrid contains no nodes. At least 1 node is required.", field_name="nodes")

    # 1. Validate Nodes
    for node_id, node in grid.nodes.items():
        if not isinstance(node, GridNode):
            raise PipelineValidationError(
                f"Node '{node_id}' is not an instance of GridNode.",
                field_name=f"nodes.{node_id}",
            )
        if node.id != node_id:
            raise PipelineValidationError(
                f"Node key mismatch: dictionary key '{node_id}' != node.id '{node.id}'.",
                field_name=f"nodes.{node_id}",
            )

        # Numerical validation
        gen = node.operational.generation_mw
        dem = node.operational.demand_mw
        cap = node.operational.max_capacity_mw
        v_kv = node.operational.voltage_kv

        for val_name, val in [("generation_mw", gen), ("demand_mw", dem), ("max_capacity_mw", cap), ("voltage_kv", v_kv)]:
            if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                raise PipelineValidationError(
                    f"Node '{node_id}' has invalid numeric value for '{val_name}': {val}.",
                    field_name=f"nodes.{node_id}.{val_name}",
                )
            if val < 0.0:
                raise PipelineValidationError(
                    f"Node '{node_id}' has negative value for '{val_name}': {val}. Values must be >= 0.",
                    field_name=f"nodes.{node_id}.{val_name}",
                )

    # 2. Validate Lines
    for line_id, line in grid.lines.items():
        if not isinstance(line, TransmissionLine):
            raise PipelineValidationError(
                f"Line '{line_id}' is not an instance of TransmissionLine.",
                field_name=f"lines.{line_id}",
            )
        if line.id != line_id:
            raise PipelineValidationError(
                f"Line key mismatch: dictionary key '{line_id}' != line.id '{line.id}'.",
                field_name=f"lines.{line_id}",
            )
        if line.source_node_id not in grid.nodes:
            raise PipelineValidationError(
                f"Line '{line_id}' references non-existent source node '{line.source_node_id}'.",
                field_name=f"lines.{line_id}.source_node_id",
            )
        if line.target_node_id not in grid.nodes:
            raise PipelineValidationError(
                f"Line '{line_id}' references non-existent target node '{line.target_node_id}'.",
                field_name=f"lines.{line_id}.target_node_id",
            )
        if line.capacity_mw <= 0.0 or math.isnan(line.capacity_mw) or math.isinf(line.capacity_mw):
            raise PipelineValidationError(
                f"Line '{line_id}' has invalid capacity_mw: {line.capacity_mw}. Capacity must be > 0.",
                field_name=f"lines.{line_id}.capacity_mw",
            )
        if line.reactance_ohm < 0.0 or math.isnan(line.reactance_ohm) or math.isinf(line.reactance_ohm):
            raise PipelineValidationError(
                f"Line '{line_id}' has invalid reactance_ohm: {line.reactance_ohm}. Reactance must be >= 0.",
                field_name=f"lines.{line_id}.reactance_ohm",
            )


def validate_pipeline_config(config: PipelineConfig, grid: Optional[ElectricityGrid] = None) -> None:
    """
    Validates pipeline execution parameters.

    Raises:
        PipelineValidationError: If configuration options are out of bounds.
    """
    if config.forecast_horizon_hours <= 0:
        raise PipelineValidationError(
            f"forecast_horizon_hours must be a positive integer, got {config.forecast_horizon_hours}.",
            field_name="config.forecast_horizon_hours",
        )
    if config.forecast_horizon_hours > 168:
        raise PipelineValidationError(
            f"forecast_horizon_hours cannot exceed 168 hours (7 days), got {config.forecast_horizon_hours}.",
            field_name="config.forecast_horizon_hours",
        )
    if config.n_1_top_k < 0:
        raise PipelineValidationError(
            f"n_1_top_k must be non-negative, got {config.n_1_top_k}.",
            field_name="config.n_1_top_k",
        )
    if config.ranked_components_top_k < 0:
        raise PipelineValidationError(
            f"ranked_components_top_k must be non-negative, got {config.ranked_components_top_k}.",
            field_name="config.ranked_components_top_k",
        )
    if config.monte_carlo_trials < 1:
        raise PipelineValidationError(
            f"monte_carlo_trials must be at least 1, got {config.monte_carlo_trials}.",
            field_name="config.monte_carlo_trials",
        )

    # Validate trigger lines if provided
    if config.cascading_trigger_lines and grid is not None:
        for lid in config.cascading_trigger_lines:
            if lid not in grid.lines and lid not in grid.nodes:
                raise PipelineValidationError(
                    f"Cascading trigger line/asset '{lid}' not found in grid.",
                    field_name="config.cascading_trigger_lines",
                )


def validate_telemetry(telemetry: Dict[str, Any], grid: ElectricityGrid) -> None:
    """
    Validates optional live telemetry dictionary.
    Format expected:
      {
        "nodes": { "node_id": {"demand_mw": float, "generation_mw": float, ...} },
        "lines": { "line_id": {"current_flow_mw": float, ...} }
      }
    """
    if not isinstance(telemetry, dict):
        raise PipelineValidationError(
            f"Telemetry must be a dictionary, got {type(telemetry).__name__}.",
            field_name="telemetry",
        )

    if "nodes" in telemetry and isinstance(telemetry["nodes"], dict):
        for nid, node_data in telemetry["nodes"].items():
            if nid not in grid.nodes:
                raise PipelineValidationError(
                    f"Telemetry references unknown node ID '{nid}'.",
                    field_name=f"telemetry.nodes.{nid}",
                )
            for key, val in node_data.items():
                if isinstance(val, (int, float)) and (math.isnan(val) or math.isinf(val) or val < 0):
                    raise PipelineValidationError(
                        f"Telemetry for node '{nid}' has invalid numeric value for '{key}': {val}.",
                        field_name=f"telemetry.nodes.{nid}.{key}",
                    )

    if "lines" in telemetry and isinstance(telemetry["lines"], dict):
        for lid, line_data in telemetry["lines"].items():
            if lid not in grid.lines:
                raise PipelineValidationError(
                    f"Telemetry references unknown line ID '{lid}'.",
                    field_name=f"telemetry.lines.{lid}",
                )
            for key, val in line_data.items():
                if isinstance(val, (int, float)) and (math.isnan(val) or math.isinf(val) or val < 0):
                    raise PipelineValidationError(
                        f"Telemetry for line '{lid}' has invalid numeric value for '{key}': {val}.",
                        field_name=f"telemetry.lines.{lid}.{key}",
                    )
