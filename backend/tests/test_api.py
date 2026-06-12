import json

from fastapi.testclient import TestClient

from app.main import create_app


def _client():
    return TestClient(create_app())


def _seed_preset(presets_dir):
    preset = {
        "id": "triangulo",
        "name": "Triangulo",
        "source": "preset",
        "symmetric": True,
        "points": [
            {"id": "a", "label": "A", "sprite": "shop", "x": 10, "y": 10},
            {"id": "b", "label": "B", "sprite": "home", "x": 90, "y": 10},
            {"id": "c", "label": "C", "sprite": "park", "x": 50, "y": 80},
        ],
        "matrix": [[0, 8, 5], [8, 0, 4], [5, 4, 0]],
    }
    (presets_dir / "triangulo.json").write_text(json.dumps(preset), encoding="utf-8")


def test_list_maps_empty(temp_store):
    r = _client().get("/maps")
    assert r.status_code == 200
    assert r.json() == []


def test_create_get_delete_roundtrip(temp_store):
    client = _client()
    body = {
        "id": "mini",
        "name": "Mini",
        "symmetric": True,
        "points": [
            {"id": "a", "label": "A", "sprite": "shop", "x": 0, "y": 0},
            {"id": "b", "label": "B", "sprite": "home", "x": 10, "y": 0},
        ],
        "matrix": [[0, 3], [3, 0]],
    }
    r = client.post("/maps", json=body)
    assert r.status_code == 201, r.text
    assert r.json()["source"] == "user"

    r = client.get("/maps/mini")
    assert r.status_code == 200
    assert r.json()["name"] == "Mini"

    r = client.delete("/maps/mini")
    assert r.status_code == 204

    r = client.get("/maps/mini")
    assert r.status_code == 404


def test_create_conflict_returns_409(temp_store):
    client = _client()
    body = {
        "id": "dup",
        "name": "Dup",
        "symmetric": True,
        "points": [
            {"id": "a", "label": "A", "sprite": "shop", "x": 0, "y": 0},
            {"id": "b", "label": "B", "sprite": "home", "x": 10, "y": 0},
        ],
        "matrix": [[0, 3], [3, 0]],
    }
    assert client.post("/maps", json=body).status_code == 201
    assert client.post("/maps", json=body).status_code == 409


def test_create_non_square_matrix_returns_422(temp_store):
    client = _client()
    body = {
        "id": "bad",
        "name": "Bad",
        "symmetric": True,
        "points": [
            {"id": "a", "label": "A", "sprite": "shop", "x": 0, "y": 0},
            {"id": "b", "label": "B", "sprite": "home", "x": 10, "y": 0},
        ],
        "matrix": [[0, 3, 9], [3, 0, 1]],
    }
    assert client.post("/maps", json=body).status_code == 422


def test_delete_preset_is_forbidden(temp_store):
    presets, _ = temp_store
    _seed_preset(presets)
    assert _client().delete("/maps/triangulo").status_code == 403


def test_optimize_returns_route_and_baselines(temp_store):
    presets, _ = temp_store
    _seed_preset(presets)
    r = _client().post(
        "/optimize",
        json={
            "map_id": "triangulo",
            "stop_ids": ["a", "b", "c"],
            "start_id": "a",
            "restarts": 10,
            "seed": 1,
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["tour"][0] == "a"
    assert data["tour"][-1] == "a"
    assert len(data["tour"]) == 4  # a, b, c, a
    # 3 stops: only one distinct cycle -> optimum == brute force == 8+4+5 = 17
    assert data["total_cost"] == 17
    assert data["baselines"]["brute_force_cost"] == 17
    assert data["brute_force_skipped"] is False
    assert data["baselines"]["random_cost"] >= data["total_cost"]


def test_optimize_start_not_in_stops_returns_422(temp_store):
    presets, _ = temp_store
    _seed_preset(presets)
    r = _client().post(
        "/optimize",
        json={"map_id": "triangulo", "stop_ids": ["a", "b"], "start_id": "c"},
    )
    assert r.status_code == 422


def test_optimize_unknown_map_returns_404(temp_store):
    r = _client().post(
        "/optimize",
        json={"map_id": "ghost", "stop_ids": ["a", "b"], "start_id": "a"},
    )
    assert r.status_code == 404


def test_generate_without_save_is_not_persisted(temp_store):
    client = _client()
    r = client.post("/maps/generate", json={"n": 5, "seed": 2})
    assert r.status_code == 200
    assert r.json()["source"] == "generated"
    assert len(r.json()["points"]) == 5
    assert client.get("/maps").json() == []


def test_generate_with_save_is_persisted(temp_store):
    client = _client()
    r = client.post("/maps/generate", json={"n": 4, "seed": 2, "save": True, "id": "g4", "name": "G4"})
    assert r.status_code == 200
    assert any(s["id"] == "g4" for s in client.get("/maps").json())
