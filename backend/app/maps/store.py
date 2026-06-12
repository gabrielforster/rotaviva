"""JSON file store for maps: read-only presets + CRUD user maps.

This is the ONLY module that touches the filesystem. The routing core never
imports it. All filesystem-shaped failures are raised as MapError subclasses;
the API layer translates them to HTTP status codes.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.maps.grid import GridError, parse_grid, validate_points


class MapError(Exception):
    """Base class for map-store errors."""


class MapNotFound(MapError):
    pass


class MapConflict(MapError):
    pass


class MapValidationError(MapError):
    pass


class PresetReadOnly(MapError):
    pass


_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_map(data: dict[str, Any]) -> None:
    """Structurally validate a grid map dict; raise ``MapValidationError``."""
    map_id = data.get("id")
    if not isinstance(map_id, str) or not _SLUG_RE.match(map_id):
        raise MapValidationError("id must be a lowercase slug (a-z, 0-9, hyphens)")
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise MapValidationError("name must be a non-empty string")
    if data.get("style") not in ("city", "warehouse"):
        raise MapValidationError("style must be 'city' or 'warehouse'")

    grid_data = data.get("grid")
    if not isinstance(grid_data, dict):
        raise MapValidationError("grid must be an object with cells and cell_size")
    try:
        grid = parse_grid(list(grid_data.get("cells", [])), int(grid_data.get("cell_size", 40)))
    except (GridError, TypeError, ValueError) as exc:
        raise MapValidationError(str(exc)) from exc

    points = data.get("points")
    if not isinstance(points, list) or len(points) < 2:
        raise MapValidationError("points must be a list of at least 2 points")
    seen: set[str] = set()
    cells: list[tuple[int, int]] = []
    for point in points:
        if not isinstance(point, dict):
            raise MapValidationError("each point must be an object")
        pid = point.get("id")
        if not isinstance(pid, str) or not pid:
            raise MapValidationError("each point needs a non-empty string id")
        if pid in seen:
            raise MapValidationError(f"duplicate point id: {pid}")
        seen.add(pid)
        cell = point.get("cell")
        if not isinstance(cell, dict) or not isinstance(cell.get("row"), int) or not isinstance(cell.get("col"), int):
            raise MapValidationError(f"point {pid} needs an integer cell {{row, col}}")
        cells.append((cell["row"], cell["col"]))

    try:
        validate_points(grid, cells)
    except GridError as exc:
        raise MapValidationError(str(exc)) from exc


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _preset_maps() -> dict[str, dict[str, Any]]:
    presets_dir = get_settings().presets_dir
    result: dict[str, dict[str, Any]] = {}
    if not presets_dir.is_dir():
        return result
    for path in sorted(presets_dir.glob("*.json")):
        data = _read_json(path)
        data["source"] = "preset"
        result[data["id"]] = data
    return result


def _user_maps() -> dict[str, dict[str, Any]]:
    data_dir = get_settings().data_dir
    result: dict[str, dict[str, Any]] = {}
    if not data_dir.is_dir():
        return result
    for path in sorted(data_dir.glob("*.json")):
        data = _read_json(path)
        result[data["id"]] = data
    return result


def _all_maps() -> dict[str, dict[str, Any]]:
    maps = _preset_maps()
    maps.update(_user_maps())  # user maps shadow nothing: ids are unique across both
    return maps


def list_maps() -> list[dict[str, Any]]:
    """Summary form of every map (presets + user), sorted by name."""
    summaries = [
        {
            "id": m["id"],
            "name": m.get("name", m["id"]),
            "source": m.get("source", "user"),
            "point_count": len(m.get("points", [])),
        }
        for m in _all_maps().values()
    ]
    return sorted(summaries, key=lambda s: s["name"].lower())


def get_map(map_id: str) -> dict[str, Any]:
    """Full map by id; raise ``MapNotFound`` if absent."""
    maps = _all_maps()
    if map_id not in maps:
        raise MapNotFound(f"map not found: {map_id}")
    return maps[map_id]


def create_map(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and persist a new user map; raise on collision/validation/IO."""
    validate_map(data)
    map_id = data["id"]
    existing = _all_maps()
    if map_id in existing:
        raise MapConflict(f"map id already exists: {map_id}")
    new_name = data["name"].strip().lower()
    for other in existing.values():
        if other.get("name", "").strip().lower() == new_name:
            raise MapConflict(f"map name already exists: {data['name']}")
    # A registration can never claim preset status.
    if data.get("source") not in ("user", "generated"):
        data["source"] = "user"
    settings = get_settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    path = settings.data_dir / f"{map_id}.json"
    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
    except OSError as exc:  # disk full, permissions, etc.
        raise MapError(f"failed to write map: {exc}") from exc
    return data


def delete_map(map_id: str) -> None:
    """Delete a user map; reject presets and unknown ids."""
    if map_id in _preset_maps():
        raise PresetReadOnly(f"preset maps cannot be deleted: {map_id}")
    path = get_settings().data_dir / f"{map_id}.json"
    if not path.exists():
        raise MapNotFound(f"map not found: {map_id}")
    path.unlink()
