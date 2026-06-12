"""Pure tour representation and cost — no I/O, deterministic.

A tour is a list of integer indices into a distance matrix, forming a closed
cycle. The start is fixed at position 0. The cycle implicitly closes from the
last element back to the first; that closing edge is included in the cost.
"""
from __future__ import annotations

Matrix = list[list[float]]
Tour = list[int]


def tour_cost(matrix: Matrix, tour: Tour) -> float:
    """Total round-trip cost of a closed tour.

    Sums the directed edge ``matrix[tour[i]][tour[i+1]]`` around the cycle,
    including the closing edge ``matrix[tour[-1]][tour[0]]``. Works for both
    symmetric and asymmetric matrices.
    """
    n = len(tour)
    total = 0.0
    for i in range(n):
        a = tour[i]
        b = tour[(i + 1) % n]
        total += matrix[a][b]
    return total
