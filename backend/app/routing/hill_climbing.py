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
