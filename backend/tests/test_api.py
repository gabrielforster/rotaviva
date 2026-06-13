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


def test_create_then_optimize_uses_grid_distance(client):
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
