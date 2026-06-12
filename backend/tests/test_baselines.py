import math

import pytest

from app.routing.baselines import random_route_cost, brute_force_optimal
from app.routing.tour import tour_cost


def _circle_matrix(n: int) -> list[list[float]]:
    pts = [
        (math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n))
        for k in range(n)
    ]
    return [[math.dist(pts[i], pts[j]) for j in range(n)] for i in range(n)]


def test_random_route_cost_is_deterministic_and_valid():
    matrix = _circle_matrix(6)
    a = random_route_cost(matrix, 6, seed=11)
    b = random_route_cost(matrix, 6, seed=11)
    assert a == b
    # It must equal the cost of *some* valid tour, hence >= the optimum.
    assert a >= brute_force_optimal(matrix, 6)


def test_brute_force_matches_known_optimum_small_n():
    n = 6
    matrix = _circle_matrix(n)
    chord = 2 * math.sin(math.pi / n)
    assert brute_force_optimal(matrix, n) == pytest.approx(n * chord, rel=1e-9)


def test_brute_force_two_and_one_stops():
    assert brute_force_optimal([[0, 7], [7, 0]], 2) == 14
    assert brute_force_optimal([[0]], 1) == 0


def test_brute_force_guard_skips_large_n():
    # n == guard -> skipped (None). Matrix content is irrelevant when skipped.
    big = [[0] * 10 for _ in range(10)]
    assert brute_force_optimal(big, 10, guard=10) is None
    # n just below the guard still computes.
    small = [[0] * 9 for _ in range(9)]
    assert brute_force_optimal(small, 9, guard=10) == 0
