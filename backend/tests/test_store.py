import json

import pytest

from app.maps import store


def _grid_map(**over):
    data = {
        "id": "m1",
        "name": "M1",
        "style": "city",
        "grid": {"cell_size": 40, "cells": ["...", "...", "..."]},
        "points": [
            {"id": "a", "label": "A", "sprite": "factory", "cell": {"row": 0, "col": 0}},
            {"id": "b", "label": "B", "sprite": "shop", "cell": {"row": 2, "col": 2}},
        ],
    }
    data.update(over)
    return data


def test_validate_accepts_good_grid_map():
    store.validate_map(_grid_map())  # no raise


def test_validate_rejects_bad_slug():
    with pytest.raises(store.MapValidationError):
        store.validate_map(_grid_map(id="Bad ID"))


def test_validate_rejects_bad_style():
    with pytest.raises(store.MapValidationError):
        store.validate_map(_grid_map(style="village"))


def test_validate_rejects_point_on_wall():
    bad = _grid_map(grid={"cell_size": 40, "cells": ["...", ".#.", "..."]})
    bad["points"][1]["cell"] = {"row": 1, "col": 1}
    with pytest.raises(store.MapValidationError):
        store.validate_map(bad)


def test_validate_rejects_disconnected_points():
    bad = _grid_map(grid={"cell_size": 40, "cells": ["..#..", "..#..", "..#.."]})
    bad["points"] = [
        {"id": "a", "label": "A", "sprite": "pin", "cell": {"row": 0, "col": 0}},
        {"id": "b", "label": "B", "sprite": "pin", "cell": {"row": 0, "col": 4}},
    ]
    with pytest.raises(store.MapValidationError):
        store.validate_map(bad)


def test_create_persists_without_matrix(temp_store):
    _, data_dir = temp_store
    store.create_map(_grid_map())
    saved = json.loads((data_dir / "m1.json").read_text())
    assert "matrix" not in saved
    assert saved["grid"]["cells"] == ["...", "...", "..."]


def test_create_then_get_roundtrip(temp_store):
    store.create_map(_grid_map())
    got = store.get_map("m1")
    assert got["style"] == "city" and len(got["points"]) == 2


def test_create_rejects_duplicate_id(temp_store):
    store.create_map(_grid_map())
    with pytest.raises(store.MapConflict):
        store.create_map(_grid_map(name="Different"))


from pathlib import Path

from app.maps.grid import matrix_for_map


def test_bundled_presets_are_valid_and_derivable():
    # Uses the real presets dir (no temp_store fixture).
    presets = {m["id"]: m for m in [store.get_map("centro"), store.get_map("galpao-central")]}
    assert presets["centro"]["style"] == "city"
    assert presets["galpao-central"]["style"] == "warehouse"
    for m in presets.values():
        store.validate_map(m)            # structurally valid
        matrix = matrix_for_map(m)       # connected -> derivable
        assert len(matrix) == len(m["points"])
