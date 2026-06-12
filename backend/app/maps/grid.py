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
