"""Hill Climbing with Random Restart over a 2-opt neighborhood.

Pure Python, no I/O, deterministic under a provided seed.
"""
from __future__ import annotations

import random
from collections.abc import Iterator
from dataclasses import dataclass

from .tour import Matrix, Tour, tour_cost


@dataclass(frozen=True)
class HillClimbResult:
    """Outcome of a random-restart run, with telemetry for the evolution chart.

    ``full_history`` is every accepted-move cost concatenated across all restarts
    (the sawtooth). ``restart_indices[k]`` is the position in ``full_history``
    where restart ``k`` begins. ``min(full_history) == best_cost``.
    """
    best_tour: Tour
    best_cost: float
    full_history: list[float]
    restart_indices: list[int]


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
) -> tuple[Tour, float, list[float]]:
    """Best-improving 2-opt local search; also returns the accepted-cost trace.

    The trace starts with the initial tour's cost and appends the cost after
    each accepted improving move, so it is a non-increasing sequence describing
    this single climb. Search behavior is otherwise unchanged.
    """
    current = list(tour)
    current_cost = tour_cost(matrix, current)
    visited.add(tuple(current))
    trace = [current_cost]
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
            return current, current_cost, trace
        current = best_neighbor
        current_cost = best_cost
        trace.append(current_cost)


def hill_climb(
    matrix: Matrix, n: int, restarts: int, seed: int | None = None
) -> HillClimbResult:
    """Run Random-Restart Hill Climbing; return a :class:`HillClimbResult`.

    Each restart begins from a fresh seeded random tour; the run-wide ``visited``
    set is shared so identical tours are never re-evaluated. ``full_history``
    concatenates every restart's accepted-cost trace and ``restart_indices``
    records where each restart begins. Deterministic for a fixed ``seed``.
    """
    rng = random.Random(seed)
    visited: set[tuple[int, ...]] = set()
    best_tour: Tour = list(range(n))
    best_cost = float("inf")
    full_history: list[float] = []
    restart_indices: list[int] = []
    for _ in range(max(1, restarts)):
        restart_indices.append(len(full_history))
        candidate, cost, trace = local_search(matrix, random_tour(n, rng), visited)
        full_history.extend(trace)
        if cost < best_cost:
            best_cost = cost
            best_tour = candidate
    return HillClimbResult(best_tour, best_cost, full_history, restart_indices)
