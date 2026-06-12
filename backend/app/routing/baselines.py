"""Baseline route costs for benchmarking the agent.

Pure Python, no I/O. ``random_route_cost`` is the "no intelligence" baseline;
``brute_force_optimal`` is the exact optimum, guarded to small N.
"""
from __future__ import annotations

import itertools
import random

from .tour import Matrix, tour_cost


def random_route_cost(matrix: Matrix, n: int, seed: int | None = None) -> float:
    """Cost of a single random valid tour (start fixed at position 0), seeded."""
    rng = random.Random(seed)
    rest = list(range(1, n))
    rng.shuffle(rest)
    return tour_cost(matrix, [0, *rest])


def brute_force_optimal(matrix: Matrix, n: int, guard: int = 10) -> float | None:
    """Exact optimal round-trip cost via permutations, or ``None`` when skipped.

    Returns ``None`` when ``n >= guard`` (too large to enumerate). Otherwise
    returns the minimum tour cost over all permutations with the start fixed at 0.
    """
    if n >= guard:
        return None
    best = float("inf")
    for perm in itertools.permutations(range(1, n)):
        best = min(best, tour_cost(matrix, [0, *perm]))
    return best
