"""Hill Climbing with Random Restart over a 2-opt neighborhood.

Pure Python, no I/O, deterministic under a provided seed.
"""
from __future__ import annotations

import random
from collections.abc import Iterator

from .tour import Matrix, Tour, tour_cost


def two_opt_neighbors(tour: Tour) -> Iterator[Tour]:
    """Yield every 2-opt neighbor of ``tour``, keeping the start (position 0) fixed.

    A 2-opt move reverses the contiguous segment between positions ``i`` and
    ``j`` (``1 <= i < j < len(tour)``). Position 0 is never moved, so the start
    stays fixed and every neighbor is a valid permutation visiting each stop once.
    """
    n = len(tour)
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            yield tour[:i] + tour[i : j + 1][::-1] + tour[j + 1 :]


def random_tour(n: int, rng: random.Random) -> Tour:
    """A random tour over indices ``0..n-1`` with the start (0) fixed at position 0."""
    rest = list(range(1, n))
    rng.shuffle(rest)
    return [0] + rest


def local_search(
    matrix: Matrix, tour: Tour, visited: set[tuple[int, ...]]
) -> tuple[Tour, float]:
    """Best-improving 2-opt local search from ``tour`` until a local optimum.

    ``visited`` is the run-wide memory of canonical tour keys already evaluated;
    neighbors whose key is in ``visited`` are skipped (never re-evaluated), which
    is the concept doc's "memória de estados". The search moves to the strictly
    best-improving unvisited neighbor and stops when none improves on the current
    cost. Cost strictly decreases on every accepted move, so it always terminates.
    """
    current = list(tour)
    current_cost = tour_cost(matrix, current)
    visited.add(tuple(current))
    while True:
        best_neighbor: Tour | None = None
        best_cost = current_cost
        for neighbor in two_opt_neighbors(current):
            key = tuple(neighbor)
            if key in visited:
                continue
            visited.add(key)
            cost = tour_cost(matrix, neighbor)
            if cost < best_cost:
                best_cost = cost
                best_neighbor = neighbor
        if best_neighbor is None:
            return current, current_cost
        current = best_neighbor
        current_cost = best_cost


def hill_climb(
    matrix: Matrix, n: int, restarts: int, seed: int | None = None
) -> tuple[Tour, float, list[float]]:
    """Run Random-Restart Hill Climbing; return ``(best_tour, best_cost, history)``.

    ``n`` is the number of stops (``matrix`` is ``n x n``). Each restart begins
    from a fresh seeded random tour and runs ``local_search``; the run-wide
    ``visited`` set is shared across restarts so identical tours are never
    re-evaluated. ``history[k]`` is the best cost found through the end of
    restart ``k`` — a non-increasing convergence curve for the chart.
    Deterministic for a fixed ``seed``.
    """
    rng = random.Random(seed)
    visited: set[tuple[int, ...]] = set()
    best_tour: Tour = list(range(n))
    best_cost = float("inf")
    history: list[float] = []
    for _ in range(max(1, restarts)):
        candidate, cost = local_search(matrix, random_tour(n, rng), visited)
        if cost < best_cost:
            best_cost = cost
            best_tour = candidate
        history.append(best_cost)
    return best_tour, best_cost, history
