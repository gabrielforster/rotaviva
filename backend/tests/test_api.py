import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(temp_store):
    return TestClient(create_app())


def _city_payload(map_id="mine"):
    return {
        "id": map_id,
        "name": "Mine",
        "style": "city",
        "grid": {"cell_size": 40, "cells": ["...", "...", "..."]},
        "points": [
            {"id": "a", "label": "A", "sprite": "factory", "cell": {"row": 0, "col": 0}},
            {"id": "b", "label": "B", "sprite": "shop", "cell": {"row": 0, "col": 2}},
            {"id": "c", "label": "C", "sprite": "home", "cell": {"row": 2, "col": 2}},
        ],
    }


@pytest.mark.parametrize("style", ["city", "warehouse"])
def test_generate_returns_grid_map(client, style):
    r = client.post("/maps/generate", json={"style": style, "size": "small", "n": 5, "seed": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["style"] == style
    assert "matrix" not in body
    assert len(body["points"]) == 5


def test_optimize_returns_closed_integer_tour(client):
    assert client.post("/maps", json=_city_payload()).status_code == 201
    r = client.post(
        "/optimize",
        json={"map_id": "mine", "stop_ids": ["a", "b", "c"], "start_id": "a", "seed": 0},
    )
    assert r.status_code == 200
    body = r.json()
    # a(0,0) b(0,2) c(2,2): closed tour a->b->c->a = 2 + 2 + 4 = 8 steps
    assert body["total_cost"] == 8
    assert body["tour"][0] == "a" and body["tour"][-1] == "a"


def test_optimize_distance_follows_streets_not_crow_flies(client):
    # a(0,0) and b(2,0) are 2 cells apart in a straight line, but a wall at (1,0)
    # forces the route around: 4 steps each way -> closed tour costs 8, not 4.
    walled = {
        "id": "walled",
        "name": "Walled",
        "style": "city",
        "grid": {"cell_size": 40, "cells": ["...", "#..", "..."]},
        "points": [
            {"id": "a", "label": "A", "sprite": "factory", "cell": {"row": 0, "col": 0}},
            {"id": "b", "label": "B", "sprite": "shop", "cell": {"row": 2, "col": 0}},
        ],
    }
    assert client.post("/maps", json=walled).status_code == 201
    r = client.post(
        "/optimize",
        json={"map_id": "walled", "stop_ids": ["a", "b"], "start_id": "a", "seed": 0},
    )
    assert r.status_code == 200
    assert r.json()["total_cost"] == 8  # crow-flies round trip would be 4


def test_generate_with_save_persists(client):
    r = client.post(
        "/maps/generate",
        json={"style": "city", "size": "small", "n": 5, "seed": 1, "save": True,
              "id": "gen-save", "name": "Gen Save"},
    )
    assert r.status_code == 200
    assert client.get("/maps/gen-save").status_code == 200
    assert any(m["id"] == "gen-save" for m in client.get("/maps").json())


def test_generate_without_save_is_not_persisted(client):
    r = client.post(
        "/maps/generate",
        json={"style": "city", "size": "small", "n": 4, "seed": 2, "id": "gen-nosave"},
    )
    assert r.status_code == 200
    assert client.get("/maps/gen-nosave").status_code == 404


def test_delete_preset_is_forbidden(temp_store):
    presets_dir, _ = temp_store
    (presets_dir / "p.json").write_text(json.dumps(_city_payload("p")))
    bare = TestClient(create_app())
    assert bare.delete("/maps/p").status_code == 403


def test_optimize_unknown_map_is_404(client):
    r = client.post(
        "/optimize", json={"map_id": "nope", "stop_ids": ["a", "b"], "start_id": "a"}
    )
    assert r.status_code == 404


def test_optimize_start_not_in_stops_is_422(client):
    client.post("/maps", json=_city_payload("m422"))
    r = client.post(
        "/optimize",
        json={"map_id": "m422", "stop_ids": ["a", "b"], "start_id": "c"},
    )
    assert r.status_code == 422


def test_create_then_delete_roundtrip(client):
    assert client.post("/maps", json=_city_payload("crud")).status_code == 201
    assert client.delete("/maps/crud").status_code == 204
    assert client.get("/maps/crud").status_code == 404


def test_create_rejects_disconnected(client):
    bad = _city_payload("walled")
    bad["grid"]["cells"] = ["..#..", "..#..", "..#.."]
    bad["points"] = [
        {"id": "a", "label": "A", "sprite": "pin", "cell": {"row": 0, "col": 0}},
        {"id": "b", "label": "B", "sprite": "pin", "cell": {"row": 0, "col": 4}},
        {"id": "c", "label": "C", "sprite": "pin", "cell": {"row": 2, "col": 4}},
    ]
    assert client.post("/maps", json=bad).status_code == 422


def test_list_and_get_presets():
    # Uses the real bundled presets dir (no temp_store), so presets are visible.
    real_client = TestClient(create_app())
    ids = {m["id"] for m in real_client.get("/maps").json()}
    assert {"centro", "galpao-central"} <= ids
    assert real_client.get("/maps/centro").json()["style"] == "city"


def test_optimize_persists_run_and_returns_matrix(client):
    assert client.post("/maps", json=_city_payload()).status_code == 201
    body = {"map_id": "mine", "stop_ids": ["a", "b", "c"], "start_id": "a"}
    res = client.post("/optimize", json=body)
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data["run_id"], int) and data["run_id"] >= 1
    assert data["tour"][0] == data["tour"][-1] == "a"
    assert len(data["matrix"]) == len(data["stop_order"]) == 3
    assert data["stop_labels"] and "history" not in data


def test_runs_list_detail_and_delete(client):
    assert client.post("/maps", json=_city_payload()).status_code == 201
    body = {"map_id": "mine", "stop_ids": ["a", "b", "c"], "start_id": "a"}
    run_id = client.post("/optimize", json=body).json()["run_id"]
    listed = client.get("/runs").json()
    assert any(r["id"] == run_id and r["stop_count"] == 3 for r in listed)
    detail = client.get(f"/runs/{run_id}").json()
    assert detail["id"] == run_id and detail["matrix"]
    # the run carries a self-contained map snapshot (only its stops) for the map view
    assert detail["map"]["grid"]["cells"]
    assert {p["id"] for p in detail["map"]["points"]} == set(detail["stop_order"])
    assert all("cell" in p for p in detail["map"]["points"])
    assert client.delete(f"/runs/{run_id}").status_code == 204
    assert client.get(f"/runs/{run_id}").status_code == 404


def test_run_chart_endpoints_return_png(client):
    assert client.post("/maps", json=_city_payload()).status_code == 201
    body = {"map_id": "mine", "stop_ids": ["a", "b", "c"], "start_id": "a"}
    run_id = client.post("/optimize", json=body).json()["run_id"]
    for suffix in ("route.png", "evolution.png"):
        r = client.get(f"/runs/{run_id}/{suffix}")
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"
        assert r.content.startswith(b"\x89PNG")


def test_run_detail_unknown_is_404(client):
    assert client.get("/runs/123456").status_code == 404
