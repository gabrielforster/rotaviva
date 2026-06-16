"""Server-side chart rendering for optimization runs.

Uses matplotlib's object-oriented API (``Figure`` + ``FigureCanvasAgg``) rather
than ``pyplot``, whose global state is not thread-safe under FastAPI's sync
threadpool. Each function returns PNG bytes.
"""
from __future__ import annotations

from io import BytesIO

import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from app.maps.grid import bfs_path, cell_center, parse_grid

# Sequential green scale matching the on-screen route: medium green at the
# start of the tour, dark green at the end — the color reads as direction.
_GREEN_SCALE = LinearSegmentedColormap.from_list("rota", ["#34d399", "#166534"])


def _to_png(fig: Figure) -> bytes:
    buf = BytesIO()
    FigureCanvasAgg(fig).print_png(buf)
    return buf.getvalue()


def _tour_legs(grid, points, tour):
    """Per-leg street paths for the tour.

    Returns ``[(from_id, to_id, [cells…]), …]`` for each consecutive pair in
    ``tour``; each cell list is the BFS path (inclusive of both endpoints), or
    empty when the pair is unreachable.
    """
    by_id = {p["id"]: p for p in points}
    legs = []
    for a, b in zip(tour, tour[1:]):
        ca = (by_id[a]["cell"]["row"], by_id[a]["cell"]["col"])
        cb = (by_id[b]["cell"]["row"], by_id[b]["cell"]["col"])
        legs.append((a, b, bfs_path(grid, ca, cb) or []))
    return legs


def _green_scale_line(ax, xy, linewidth) -> None:
    """Draw a polyline through ``xy`` as a green scale (light → dark) so the
    color reads as travel direction. ``xy`` is a list of ``(x, y)`` points."""
    if len(xy) < 2:
        return
    pts = np.array(xy).reshape(-1, 1, 2)
    segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
    lc = LineCollection(
        segs, cmap=_GREEN_SCALE, linewidth=linewidth, zorder=2,
        capstyle="round", joinstyle="round",
    )
    lc.set_array(np.linspace(0, 1, len(segs)))
    ax.add_collection(lc)


def _draw_nodes(ax, grid, points, order) -> None:
    """Plot the blue stop markers with their ``"{n}. {label}"`` annotations.
    ``order`` maps a point id → its 1-based visit position."""
    for p in points:
        x, y = cell_center(grid, (p["cell"]["row"], p["cell"]["col"]))
        ax.plot(x, y, "o", color="#1f77b4", markersize=10, zorder=3)
        n = order.get(p["id"])
        text = f"{n}. {p['label']}" if n else p["label"]
        ax.annotate(text, (x, y), textcoords="offset points", xytext=(6, 6),
                    fontsize=9, color="#b91c1c", zorder=4)


def _visit_order(tour) -> dict:
    """Map each point id to its 1-based visit position from the closed tour
    (``tour[-1] == tour[0]``), so the first occurrence wins."""
    return {pid: i + 1 for i, pid in enumerate(tour[:-1])}


def _draw_route(ax, grid, points, tour) -> None:
    """Draw the grid walls, the street-following green direction-scaled route,
    and the numbered stop markers (the ``route_png`` rendering)."""
    s = grid.cell_size
    for r, row in enumerate(grid.cells):
        for c, ch in enumerate(row):
            if ch == "#":
                ax.add_patch(
                    Rectangle((c * s, r * s), s, s, facecolor="#c8cfda", edgecolor="none")
                )

    xy: list[tuple[float, float]] = []
    for _a, _b, path in _tour_legs(grid, points, tour):
        if not path:
            continue
        for cell in (path if not xy else path[1:]):
            xy.append(cell_center(grid, cell))
    _green_scale_line(ax, xy, linewidth=3)
    _draw_nodes(ax, grid, points, _visit_order(tour))


def _finish_route_axes(ax, grid, title) -> None:
    s = grid.cell_size
    ax.set_xlim(0, grid.cols * s)
    ax.set_ylim(0, grid.rows * s)
    ax.invert_yaxis()  # row 0 at the top, matching the on-screen canvas
    ax.set_aspect("equal")
    ax.set_title(title)
    # Pixel coordinates carry no meaning, so drop the axis ticks/labels entirely.
    ax.set_xticks([])
    ax.set_yticks([])


def route_png(cells, cell_size, points, tour, total_cost) -> bytes:
    """Render the street-following route over the grid.

    ``points`` is a list of ``{"id","label","cell":{"row","col"}}`` for the
    stops in the tour; ``tour`` is the closed list of point ids (last == first).
    """
    grid = parse_grid(list(cells), int(cell_size))
    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.subplots()
    _draw_route(ax, grid, points, tour)
    _finish_route_axes(ax, grid, f"Rota Otimizada (Custo: {total_cost:.0f})")
    fig.tight_layout()
    return _to_png(fig)


def route_costs_png(cells, cell_size, points, tour, total_cost, matrix, stop_order) -> bytes:
    """Render the tour as a clean node-and-edge graph (no buildings): straight
    lines connect consecutive stops, with each leg's cost printed at the segment
    midpoint.

    ``matrix`` is the pairwise cost matrix indexed by ``stop_order`` (the run's
    stop ids); a leg's cost is ``matrix[idx[a]][idx[b]]`` — the street distance
    between the two stops, independent of the straight line drawn here.
    """
    grid = parse_grid(list(cells), int(cell_size))
    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.subplots()

    center = {
        p["id"]: cell_center(grid, (p["cell"]["row"], p["cell"]["col"])) for p in points
    }
    # Straight lines between consecutive stops — no street-following, no walls.
    _green_scale_line(ax, [center[pid] for pid in tour if pid in center], linewidth=2)
    _draw_nodes(ax, grid, points, _visit_order(tour))

    idx = {pid: i for i, pid in enumerate(stop_order)}
    for a, b in zip(tour, tour[1:]):
        if a not in center or b not in center or a not in idx or b not in idx:
            continue
        cost = matrix[idx[a]][idx[b]]
        (xa, ya), (xb, yb) = center[a], center[b]
        ax.annotate(
            f"{cost:.0f}", ((xa + xb) / 2, (ya + yb) / 2),
            ha="center", va="center", fontsize=8, color="#1f2937", zorder=5,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#9ca3af", alpha=0.85),
        )

    _finish_route_axes(ax, grid, f"Rota Otimizada — Custos por Trecho (Total: {total_cost:.0f})")
    fig.tight_layout()
    return _to_png(fig)


def evolution_png(full_history, restart_indices, best_cost) -> bytes:
    """Reproduce the example evolution chart: sawtooth + restart markers + min."""
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.subplots()
    ax.plot(range(len(full_history)), full_history, color="#1f77b4", label="Custo da Rota")
    for i, pt in enumerate(restart_indices):
        ax.axvline(x=pt, color="red", linestyle="--", alpha=0.5,
                   label="Random Restart" if i == 0 else None)
    # Locate the minimum by argmin rather than ``index(best_cost)`` so a
    # re-derived/rounded ``best_cost`` can never raise ValueError.
    idx_min = min(range(len(full_history)), key=lambda i: full_history[i])
    ax.plot(idx_min, full_history[idx_min], marker="o", color="green", markersize=8,
            label="Menor Custo Absoluto")
    spread = (max(full_history) - min(full_history)) or 1.0
    ax.annotate(
        f"{best_cost:.0f}",
        xy=(idx_min, best_cost),
        xytext=(idx_min + max(1, len(full_history) // 20), best_cost + spread * 0.25),
        arrowprops=dict(facecolor="black", shrink=0.05, width=1, headwidth=6),
    )
    ax.set_title("Evolução do Custo (Hill Climbing com Random Restart)")
    ax.set_xlabel("Iterações (Total)")
    ax.set_ylabel("Custo da Rota")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return _to_png(fig)
