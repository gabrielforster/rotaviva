import json

import pytest

from app.config import get_settings
from app.maps import store


def _valid_map(map_id="cidade-x", name="Cidade X"):
    return {
        "id": map_id,
        "name": name,
        "source": "user",
        "symmetric": True,
        "points": [
            {"id": "a", "label": "A", "sprite": "shop", "x": 10, "y": 10},
            {"id": "b", "label": "B", "sprite": "home", "x": 90, "y": 20},
            {"id": "c", "label": "C", "sprite": "park", "x": 50, "y": 80},
        ],
        "matrix": [[0, 5, 7], [5, 0, 3], [7, 3, 0]],
    }


def test_settings_read_env(temp_store):
    presets, data = temp_store
    settings = get_settings()
    assert settings.presets_dir == presets
    assert settings.data_dir == data
    assert settings.brute_force_guard == 10
    assert settings.default_restarts == 20


def test_list_maps_empty(temp_store):
    assert store.list_maps() == []


def test_create_and_get_and_list(temp_store):
    created = store.create_map(_valid_map())
    assert created["source"] == "user"
    fetched = store.get_map("cidade-x")
    assert fetched["name"] == "Cidade X"
    summaries = store.list_maps()
    assert summaries == [
        {"id": "cidade-x", "name": "Cidade X", "source": "user", "point_count": 3}
    ]


def test_create_persists_to_data_dir(temp_store):
    _, data = temp_store
    store.create_map(_valid_map())
    on_disk = json.loads((data / "cidade-x.json").read_text(encoding="utf-8"))
    assert on_disk["id"] == "cidade-x"


def test_create_rejects_id_collision(temp_store):
    store.create_map(_valid_map())
    with pytest.raises(store.MapConflict):
        store.create_map(_valid_map())


def test_create_rejects_name_collision(temp_store):
    store.create_map(_valid_map(map_id="one", name="Same Name"))
    with pytest.raises(store.MapConflict):
        store.create_map(_valid_map(map_id="two", name="same name"))


def test_create_rejects_non_square_matrix(temp_store):
    bad = _valid_map()
    bad["matrix"] = [[0, 5], [5, 0]]  # 2x2 for 3 points
    with pytest.raises(store.MapValidationError):
        store.create_map(bad)


def test_create_rejects_bad_slug(temp_store):
    bad = _valid_map(map_id="Not A Slug")
    with pytest.raises(store.MapValidationError):
        store.create_map(bad)


def test_create_rejects_duplicate_point_ids(temp_store):
    bad = _valid_map()
    bad["points"][1]["id"] = "a"
    with pytest.raises(store.MapValidationError):
        store.create_map(bad)


def test_get_unknown_raises_not_found(temp_store):
    with pytest.raises(store.MapNotFound):
        store.get_map("nope")


def test_delete_user_map(temp_store):
    store.create_map(_valid_map())
    store.delete_map("cidade-x")
    with pytest.raises(store.MapNotFound):
        store.get_map("cidade-x")


def test_delete_unknown_raises_not_found(temp_store):
    with pytest.raises(store.MapNotFound):
        store.delete_map("nope")


def test_preset_is_read_only_and_listed(temp_store):
    presets, _ = temp_store
    (presets / "demo.json").write_text(
        json.dumps(_valid_map(map_id="demo", name="Demo")), encoding="utf-8"
    )
    summaries = store.list_maps()
    assert any(s["id"] == "demo" and s["source"] == "preset" for s in summaries)
    with pytest.raises(store.PresetReadOnly):
        store.delete_map("demo")


def test_cannot_register_over_a_preset_id(temp_store):
    presets, _ = temp_store
    (presets / "demo.json").write_text(
        json.dumps(_valid_map(map_id="demo", name="Demo")), encoding="utf-8"
    )
    with pytest.raises(store.MapConflict):
        store.create_map(_valid_map(map_id="demo", name="Other"))
