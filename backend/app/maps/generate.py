"""Procedural grid map generation: city blocks or warehouse racks.

Deterministic for a fixed seed. Always yields a single connected street/aisle
network with exactly ``n`` points on free cells (subject to available space).
"""
from __future__ import annotations

import random
from typing import Any

_CITY_SPRITES = ["shop", "home", "school", "hospital", "park"]
_WAREHOUSE_SPRITES = ["pin", "shop", "home"]

# (cols, rows)
SIZES: dict[str, tuple[int, int]] = {
    "small": (10, 7),
    "medium": (13, 9),
    "large": (19, 13),
}


def _point_id(i: int) -> str:
    return chr(ord("a") + i) if i < 26 else f"p{i}"


def _carve_city(cols: int, rows: int, density: float, rng: random.Random) -> list[str]:
    # Roads on every 3rd row/col form a connected lattice. Every non-road cell is
    # adjacent to a road, so carving any of them to '.' keeps the map connected.
    grid: list[str] = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if r % 3 == 0 or c % 3 == 0:
                row.append(".")
            else:
                row.append("#" if rng.random() < density else ".")
        grid.append("".join(row))
    return grid


def _carve_warehouse(cols: int, rows: int, density: float, rng: random.Random) -> list[str]:
    # Vertical racks in odd columns; aisles in even columns + border + cross-aisles.
    period = 3 if density < 0.4 else (4 if density < 0.7 else 5)
    grid: list[str] = []
    for r in range(rows):
        row = []
        for c in range(cols):
            border = r in (0, rows - 1) or c in (0, cols - 1)
            cross_aisle = r % period == 0
            aisle_col = c % 2 == 0
            row.append("." if (border or cross_aisle or aisle_col) else "#")
        grid.append("".join(row))
    return grid


def generate_map(
    map_id: str,
    name: str,
    n: int,
    *,
    style: str = "city",
    size: str = "medium",
    density: float = 0.6,
    seed: int | None = None,
    cell_size: int = 40,
) -> dict[str, Any]:
    if style not in ("city", "warehouse"):
        raise ValueError(f"unknown style: {style}")
    cols, rows = SIZES.get(size, SIZES["medium"])
    rng = random.Random(seed)
    cells = (
        _carve_city(cols, rows, density, rng)
        if style == "city"
        else _carve_warehouse(cols, rows, density, rng)
    )
    free = [(r, c) for r in range(rows) for c in range(cols) if cells[r][c] == "."]
    n = min(n, len(free))
    chosen = rng.sample(free, n)
    sprites = _CITY_SPRITES if style == "city" else _WAREHOUSE_SPRITES
    points: list[dict[str, Any]] = []
    for i, (r, c) in enumerate(chosen):
        points.append(
            {
                "id": _point_id(i),
                "label": "Depósito" if i == 0 else f"Parada {i}",
                "sprite": "factory" if i == 0 else sprites[i % len(sprites)],
                "cell": {"row": r, "col": c},
            }
        )
    return {
        "id": map_id,
        "name": name,
        "source": "generated",
        "style": style,
        "grid": {"cell_size": cell_size, "cells": cells},
        "points": points,
    }
