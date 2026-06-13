"""Grid spatial model: cells, 4-connected BFS, derived distance matrix.

Pure (no I/O). The routing core never imports this. A grid is a list of
equal-length strings; '.' is free (street/aisle), '#' is blocked
(building/shelf). A point sits on a free cell.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

Cell = tuple[int, int]  # (row, col)


class GridError(ValueError):
    """Raised when a grid or its points are structurally invalid."""


@dataclass(frozen=True)
class Grid:
    cells: tuple[str, ...]
    cell_size: int

    @property
    def rows(self) -> int:
        return len(self.cells)

    @property
    def cols(self) -> int:
        return len(self.cells[0]) if self.cells else 0

    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_free(self, cell: Cell) -> bool:
        r, c = cell
        return self.in_bounds(cell) and self.cells[r][c] == "."


def parse_grid(cells: list[str], cell_size: int = 40) -> Grid:
    if not isinstance(cells, list) or not cells:
        raise GridError("grid cells must be a non-empty list of strings")
    width = len(cells[0])
    if width == 0:
        raise GridError("grid rows must be non-empty")
    for row in cells:
        if not isinstance(row, str) or len(row) != width:
            raise GridError("all grid rows must be strings of equal length")
        if any(ch not in ".#" for ch in row):
            raise GridError("grid cells may only contain '.' or '#'")
    if not isinstance(cell_size, int) or cell_size <= 0:
        raise GridError("cell_size must be a positive integer")
    return Grid(cells=tuple(cells), cell_size=cell_size)


def neighbors(grid: Grid, cell: Cell) -> list[Cell]:
    r, c = cell
    candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
    return [n for n in candidates if grid.is_free(n)]


def cell_center(grid: Grid, cell: Cell) -> tuple[float, float]:
    r, c = cell
    s = grid.cell_size
    return (c * s + s / 2, r * s + s / 2)


def bfs_distances(grid: Grid, start: Cell) -> dict[Cell, int]:
    """Step-count distance from ``start`` to every reachable free cell."""
    if not grid.is_free(start):
        raise GridError(f"start cell {start} is not free")
    dist: dict[Cell, int] = {start: 0}
    queue: deque[Cell] = deque([start])
    while queue:
        cur = queue.popleft()
        for nxt in neighbors(grid, cur):
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    return dist


def bfs_path(grid: Grid, start: Cell, goal: Cell) -> list[Cell] | None:
    """Shortest 4-connected path of free cells from ``start`` to ``goal``.

    Inclusive of both endpoints. Returns ``[start]`` when start == goal, and
    ``None`` when either endpoint is blocked or the goal is unreachable.
    """
    if not grid.is_free(start) or not grid.is_free(goal):
        return None
    if start == goal:
        return [start]
    prev: dict[Cell, Cell | None] = {start: None}
    queue: deque[Cell] = deque([start])
    while queue:
        cur = queue.popleft()
        if cur == goal:
            break
        for nxt in neighbors(grid, cur):
            if nxt not in prev:
                prev[nxt] = cur
                queue.append(nxt)
    if goal not in prev:
        return None
    path: list[Cell] = []
    node: Cell | None = goal
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path


def derive_matrix(grid: Grid, cells: list[Cell]) -> list[list[int]]:
    """Full symmetric step-count matrix between point cells.

    Raises ``GridError`` if any pair is mutually unreachable.
    """
    n = len(cells)
    matrix = [[0] * n for _ in range(n)]
    # Distances are symmetric (undirected grid): fill each pair from one BFS.
    for i, src in enumerate(cells):
        dist = bfs_distances(grid, src)
        for j in range(i + 1, n):
            dst = cells[j]
            if dst not in dist:
                raise GridError(f"points {i} and {j} are not connected by streets")
            matrix[i][j] = matrix[j][i] = dist[dst]
    return matrix


def validate_points(grid: Grid, cells: list[Cell]) -> None:
    """Each cell in-bounds, free, distinct, and all mutually reachable."""
    seen: set[Cell] = set()
    for cell in cells:
        if not grid.in_bounds(cell):
            raise GridError(f"point cell {cell} is out of bounds")
        if not grid.is_free(cell):
            raise GridError(f"point cell {cell} is on a blocked cell")
        if cell in seen:
            raise GridError(f"duplicate point cell {cell}")
        seen.add(cell)
    if cells:
        reach = bfs_distances(grid, cells[0])
        for cell in cells[1:]:
            if cell not in reach:
                raise GridError("all points must be connected by streets")


def matrix_for_map(data: dict) -> list[list[int]]:
    """Build the distance matrix for a stored/generated map dict."""
    grid = parse_grid(list(data["grid"]["cells"]), int(data["grid"].get("cell_size", 40)))
    cells = [(p["cell"]["row"], p["cell"]["col"]) for p in data["points"]]
    return derive_matrix(grid, cells)
