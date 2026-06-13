"""Server-side chart rendering for optimization runs.

Uses matplotlib's object-oriented API (``Figure`` + ``FigureCanvasAgg``) rather
than ``pyplot``, whose global state is not thread-safe under FastAPI's sync
threadpool. Each function returns PNG bytes.
"""
from __future__ import annotations

from io import BytesIO

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from app.maps.grid import bfs_path, cell_center, parse_grid


def _to_png(fig: Figure) -> bytes:
    buf = BytesIO()
    FigureCanvasAgg(fig).print_png(buf)
    return buf.getvalue()


def route_png(cells, cell_size, points, tour, total_cost) -> bytes:
    """Render the street-following route over the grid.

    ``points`` is a list of ``{"id","label","cell":{"row","col"}}`` for the
    stops in the tour; ``tour`` is the closed list of point ids (last == first).
    """
    grid = parse_grid(list(cells), int(cell_size))
    by_id = {p["id"]: p for p in points}
    s = grid.cell_size
    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.subplots()

    for r, row in enumerate(grid.cells):
        for c, ch in enumerate(row):
            if ch == "#":
                ax.add_patch(
                    Rectangle((c * s, r * s), s, s, facecolor="#c8cfda", edgecolor="none")
                )

    xs: list[float] = []
    ys: list[float] = []
    for a, b in zip(tour, tour[1:]):
        ca = (by_id[a]["cell"]["row"], by_id[a]["cell"]["col"])
        cb = (by_id[b]["cell"]["row"], by_id[b]["cell"]["col"])
        path = bfs_path(grid, ca, cb)
        if not path:
            continue
        for cell in (path if not xs else path[1:]):
            x, y = cell_center(grid, cell)
            xs.append(x)
            ys.append(y)
    if xs:
        ax.plot(xs, ys, color="#22c55e", linewidth=3, zorder=2)

    order = {pid: i + 1 for i, pid in enumerate(tour[:-1])}
    for p in points:
        x, y = cell_center(grid, (p["cell"]["row"], p["cell"]["col"]))
        ax.plot(x, y, "o", color="#1f77b4", markersize=10, zorder=3)
        n = order.get(p["id"])
        text = f"{n}. {p['label']}" if n else p["label"]
        ax.annotate(text, (x, y), textcoords="offset points", xytext=(6, 6),
                    fontsize=9, color="#b91c1c", zorder=4)

    ax.set_xlim(0, grid.cols * s)
    ax.set_ylim(0, grid.rows * s)
    ax.invert_yaxis()  # row 0 at the top, matching the on-screen canvas
    ax.set_aspect("equal")
    ax.set_title(f"Rota Otimizada (Custo: {total_cost:.0f})")
    ax.set_xlabel("Eixo X")
    ax.set_ylabel("Eixo Y")
    ax.grid(True, alpha=0.3)
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
    idx_min = full_history.index(best_cost)
    ax.plot(idx_min, best_cost, marker="o", color="green", markersize=8,
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
