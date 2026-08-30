"""
Unit tests for PULSEiQ Custom Grid Registry, Topological Validation, and Endpoints (Phase 1).
"""

import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.grid import (
    CustomGridCreate,
    CustomGridUpdate,
    EdgeStatus,
    GridEdge,
    GridNode,
    NodeCriticality,
    NodeStatus,
    NodeType,
)
from backend.app.services.grid_service import grid_service


@pytest.fixture(autouse=True)
def reset_grid_service():
    """Reset grid service state before each test."""
    grid_service._custom_grids.clear()
    grid_service._custom_grid_metadata.clear()
    grid_service._active_grid_id = "reference_demo_grid"
    yield
    grid_service._custom_grids.clear()
    grid_service._custom_grid_metadata.clear()
    grid_service._active_grid_id = "reference_demo_grid"


@pytest.fixture
def client():
    return TestClient(app)


def test_reference_grid_default_state(client):
    """Verify Reference Grid is active by default and returns 50 nodes."""
    res = client.get("/api/v1/grid")
    assert res.status_code == 200
    data = res.json()
    assert data["grid_id"] == "reference_demo_grid"
    assert data["is_reference"] is True
    assert data["is_active"] is True
    assert len(data["nodes"]) == 50
    assert len(data["edges"]) >= 40


def test_create_custom_grid_valid(client):
    """Verify creating a valid custom grid with generators, substations, lines, and loads."""
    payload = {
        "grid_id": "microgrid_alpha_01",
        "name": "Microgrid Alpha Island Network",
        "description": "A 3-bus solar microgrid with hospital and BESS storage.",
        "nodes": [
            {
                "id": "solar_01",
                "name": "Local Solar Array",
                "type": "solar_plant",
                "capacity_mw": 25.0,
                "current_output_mw": 20.0,
                "status": "online",
                "criticality": "medium",
                "risk_score": 0.1,
            },
            {
                "id": "sub_01",
                "name": "Distribution Substation A",
                "type": "substation",
                "capacity_mw": 50.0,
                "current_output_mw": 0.0,
                "status": "online",
                "criticality": "high",
                "risk_score": 0.15,
            },
            {
                "id": "hosp_01",
                "name": "Community Clinic",
                "type": "critical_load",
                "capacity_mw": 10.0,
                "current_output_mw": 5.0,
                "status": "online",
                "criticality": "critical",
                "risk_score": 0.05,
            },
        ],
        "edges": [
            {
                "id": "line_solar_sub",
                "source": "solar_01",
                "target": "sub_01",
                "capacity_mw": 30.0,
                "power_flow_mw": 20.0,
                "utilization_percent": 66.67,
                "status": "normal",
                "risk_score": 0.1,
            },
            {
                "id": "line_sub_hosp",
                "source": "sub_01",
                "target": "hosp_01",
                "capacity_mw": 15.0,
                "power_flow_mw": 5.0,
                "utilization_percent": 33.33,
                "status": "normal",
                "risk_score": 0.05,
            },
        ],
    }

    res = client.post("/api/v1/grid/custom", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["grid_id"] == "microgrid_alpha_01"
    assert data["name"] == "Microgrid Alpha Island Network"
    assert data["is_reference"] is False
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 2
    assert len(data["validation_errors"]) == 0
    assert data["summary"]["total_generation_mw"] == 20.0
    assert data["summary"]["total_demand_mw"] == 5.0


def test_create_custom_grid_invalid_unknown_target_rejection(client):
    """Verify rejection when transmission line references non-existent node."""
    payload = {
        "grid_id": "invalid_grid_01",
        "name": "Dangling Line Grid",
        "nodes": [
            {
                "id": "solar_01",
                "name": "Solar Array",
                "type": "solar_plant",
                "capacity_mw": 20.0,
                "current_output_mw": 15.0,
            }
        ],
        "edges": [
            {
                "id": "line_dangling",
                "source": "solar_01",
                "target": "non_existent_node",
                "capacity_mw": 25.0,
                "power_flow_mw": 10.0,
                "status": "normal",
            }
        ],
    }

    res = client.post("/api/v1/grid/custom", json=payload)
    assert res.status_code == 400
    assert "references unknown target_node_id" in res.json()["detail"]


def test_create_custom_grid_invalid_capacity_rejection(client):
    """Verify rejection when transmission line has non-positive capacity."""
    payload = {
        "grid_id": "zero_cap_grid",
        "name": "Zero Capacity Line Grid",
        "nodes": [
            {"id": "node_a", "name": "Node A", "type": "substation", "capacity_mw": 10.0, "current_output_mw": 0.0},
            {"id": "node_b", "name": "Node B", "type": "load", "capacity_mw": 10.0, "current_output_mw": 5.0},
        ],
        "edges": [
            {
                "id": "line_zero",
                "source": "node_a",
                "target": "node_b",
                "capacity_mw": 0.0,  # Invalid <= 0
                "power_flow_mw": 0.0,
            }
        ],
    }

    res = client.post("/api/v1/grid/custom", json=payload)
    assert res.status_code == 400
    assert "non-positive capacity" in res.json()["detail"]


def test_create_custom_grid_reserved_id_rejection(client):
    """Verify cannot create a custom grid with the reserved reference grid ID."""
    payload = {
        "grid_id": "reference_demo_grid",
        "name": "Attempt Overwrite",
        "nodes": [{"id": "n1", "name": "Node 1", "type": "substation", "capacity_mw": 10.0, "current_output_mw": 0.0}],
    }
    res = client.post("/api/v1/grid/custom", json=payload)
    assert res.status_code == 400
    assert "reserved" in res.json()["detail"].lower()


def test_list_grids_contains_reference_and_custom(client):
    """Verify GET /api/v1/grid/custom returns reference grid plus created custom grids."""
    # List initial
    res1 = client.get("/api/v1/grid/custom")
    assert res1.status_code == 200
    grids1 = res1.json()
    assert len(grids1) == 1
    assert grids1[0]["grid_id"] == "reference_demo_grid"
    assert grids1[0]["is_reference"] is True
    assert grids1[0]["is_active"] is True

    # Create custom grid
    client.post(
        "/api/v1/grid/custom",
        json={
            "grid_id": "grid_beta_01",
            "name": "Grid Beta",
            "nodes": [{"id": "b1", "name": "Bus 1", "type": "substation", "capacity_mw": 50.0, "current_output_mw": 0.0}],
        },
    )

    # List updated
    res2 = client.get("/api/v1/grid/custom")
    assert res2.status_code == 200
    grids2 = res2.json()
    assert len(grids2) == 2
    ids = [g["grid_id"] for g in grids2]
    assert "reference_demo_grid" in ids
    assert "grid_beta_01" in ids


def test_get_grid_detail_by_id(client):
    """Verify retrieving specific grid details by ID."""
    # Reference grid
    res_ref = client.get("/api/v1/grid/custom/reference_demo_grid")
    assert res_ref.status_code == 200
    assert res_ref.json()["grid_id"] == "reference_demo_grid"
    assert res_ref.json()["is_reference"] is True

    # Custom grid
    client.post(
        "/api/v1/grid/custom",
        json={
            "grid_id": "grid_gamma_01",
            "name": "Grid Gamma",
            "nodes": [{"id": "g1", "name": "Bus G1", "type": "conventional_generator", "capacity_mw": 100.0, "current_output_mw": 80.0}],
        },
    )
    res_custom = client.get("/api/v1/grid/custom/grid_gamma_01")
    assert res_custom.status_code == 200
    assert res_custom.json()["grid_id"] == "grid_gamma_01"
    assert res_custom.json()["name"] == "Grid Gamma"

    # Non-existent
    res_404 = client.get("/api/v1/grid/custom/non_existent_grid")
    assert res_404.status_code == 404


def test_update_custom_grid(client):
    """Verify updating custom grid topology and properties."""
    client.post(
        "/api/v1/grid/custom",
        json={
            "grid_id": "grid_delta_01",
            "name": "Original Name",
            "nodes": [{"id": "d1", "name": "Bus D1", "type": "substation", "capacity_mw": 50.0, "current_output_mw": 0.0}],
        },
    )

    update_payload = {
        "name": "Updated Microgrid Delta",
        "description": "Expanded with new load bus",
        "nodes": [
            {"id": "d1", "name": "Bus D1", "type": "substation", "capacity_mw": 50.0, "current_output_mw": 0.0},
            {"id": "d2", "name": "Bus D2 (Load)", "type": "load", "capacity_mw": 20.0, "current_output_mw": 12.0},
        ],
        "edges": [
            {"id": "line_d1_d2", "source": "d1", "target": "d2", "capacity_mw": 25.0, "power_flow_mw": 12.0}
        ],
    }

    res = client.put("/api/v1/grid/custom/grid_delta_01", json=update_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Updated Microgrid Delta"
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1

    # Attempt to update reference grid must be rejected
    res_ref = client.put("/api/v1/grid/custom/reference_demo_grid", json={"name": "Hacked Ref"})
    assert res_ref.status_code == 400


def test_delete_custom_grid(client):
    """Verify deleting custom grid and ensuring fallback to reference grid if active."""
    client.post(
        "/api/v1/grid/custom",
        json={
            "grid_id": "grid_to_delete",
            "name": "Temporary Grid",
            "nodes": [{"id": "t1", "name": "Bus T1", "type": "substation", "capacity_mw": 10.0, "current_output_mw": 0.0}],
        },
    )

    # Activate it
    client.post("/api/v1/grid/active/grid_to_delete")
    assert grid_service.get_active_grid_id() == "grid_to_delete"

    # Delete it
    res = client.delete("/api/v1/grid/custom/grid_to_delete")
    assert res.status_code == 200
    assert res.json()["status"] == "deleted"

    # Active grid resets to reference demo grid
    assert grid_service.get_active_grid_id() == "reference_demo_grid"

    # Trying to delete reference demo grid must be rejected
    res_ref_del = client.delete("/api/v1/grid/custom/reference_demo_grid")
    assert res_ref_del.status_code == 400


def test_activate_grid(client):
    """Verify switching active grid between Reference and Custom grids."""
    client.post(
        "/api/v1/grid/custom",
        json={
            "grid_id": "microgrid_test_switch",
            "name": "Switch Test Microgrid",
            "nodes": [
                {"id": "gen_test", "name": "Gen 1", "type": "conventional_generator", "capacity_mw": 100.0, "current_output_mw": 80.0},
                {"id": "load_test", "name": "Load 1", "type": "load", "capacity_mw": 90.0, "current_output_mw": 75.0},
            ],
            "edges": [
                {"id": "line_gt", "source": "gen_test", "target": "load_test", "capacity_mw": 120.0, "power_flow_mw": 75.0}
            ],
        },
    )

    # 1. Activate Custom Grid
    res_act = client.post("/api/v1/grid/active/microgrid_test_switch")
    assert res_act.status_code == 200
    assert res_act.json()["active_grid_id"] == "microgrid_test_switch"
    assert res_act.json()["is_reference"] is False

    # GET /api/v1/grid now returns the custom grid state
    res_state = client.get("/api/v1/grid")
    assert res_state.status_code == 200
    state_data = res_state.json()
    assert state_data["grid_id"] == "microgrid_test_switch"
    assert len(state_data["nodes"]) == 2
    assert state_data["summary"]["total_generation_mw"] == 80.0

    # 2. Reactivate Reference Grid
    res_ref_act = client.post("/api/v1/grid/active/reference_demo_grid")
    assert res_ref_act.status_code == 200
    assert res_ref_act.json()["active_grid_id"] == "reference_demo_grid"
    assert res_ref_act.json()["is_reference"] is True

    # GET /api/v1/grid now returns the reference demo grid state
    res_ref_state = client.get("/api/v1/grid")
    assert res_ref_state.status_code == 200
    assert res_ref_state.json()["grid_id"] == "reference_demo_grid"
    assert len(res_ref_state.json()["nodes"]) == 50
