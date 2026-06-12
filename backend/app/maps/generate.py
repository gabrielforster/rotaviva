"""Random map generation: N points in a plane with a Euclidean distance matrix."""
from __future__ import annotations

import random
from typing import Any

import numpy as np

_SPRITES = ["shop", "home", "factory", "park", "school", "hospital"]


def _point_id(i: int) -> str:
    return chr(ord("a") + i) if i < 26 else f"p{i}"


def generate_map(
    map_id: str,
    name: str,
    n: int,
    *,
    width: int = 480,
    height: int = 320,
    seed: int | None = None,
) -> dict[str, Any]:
    """Build a map of ``n`` random points with a rounded Euclidean distance matrix.

    Deterministic for a fixed ``seed``. Coordinates fall within the SVG canvas
    bounds (with a 20px margin) so the frontend can render them directly.
    """
    rng = random.Random(seed)
    points: list[dict[str, Any]] = []
    coords: list[tuple[int, int]] = []
    for i in range(n):
        x = rng.randint(20, width - 20)
        y = rng.randint(20, height - 20)
        coords.append((x, y))
        points.append(
            {
                "id": _point_id(i),
                "label": f"Ponto {i + 1}",
                "sprite": _SPRITES[i % len(_SPRITES)],
                "x": x,
                "y": y,
            }
        )
    pts = np.array(coords, dtype=float)
    diff = pts[:, None, :] - pts[None, :, :]
    dist = np.sqrt((diff**2).sum(axis=2))
    matrix = np.round(dist, 2).tolist()
    return {
        "id": map_id,
        "name": name,
        "source": "generated",
        "symmetric": True,
        "points": points,
        "matrix": matrix,
    }
