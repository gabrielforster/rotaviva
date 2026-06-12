import random
from itertools import permutations

from app.routing.hill_climbing import (
    two_opt_neighbors,
    random_tour,
)


def test_two_opt_keeps_start_fixed_and_valid_permutations():
    tour = [0, 1, 2, 3]
    neighbors = list(two_opt_neighbors(tour))
    assert neighbors, "expected at least one neighbor"
    for nb in neighbors:
        assert nb[0] == 0, "start must stay at position 0"
        assert sorted(nb) == [0, 1, 2, 3], "every neighbor is a valid permutation"


def test_two_opt_neighbor_count_for_n4():
    # 2-opt with a fixed start over 4 stops yields exactly 3 distinct neighbors.
    assert len(list(two_opt_neighbors([0, 1, 2, 3]))) == 3


def test_two_opt_specific_reversal():
    # Reversing the segment at positions 1..2 of [0,1,2,3] gives [0,2,1,3].
    assert [0, 2, 1, 3] in list(two_opt_neighbors([0, 1, 2, 3]))


def test_two_opt_no_neighbors_for_tiny_tours():
    assert list(two_opt_neighbors([0])) == []
    assert list(two_opt_neighbors([0, 1])) == []


def test_random_tour_fixes_start_and_is_permutation():
    rng = random.Random(123)
    t = random_tour(5, rng)
    assert t[0] == 0
    assert sorted(t) == [0, 1, 2, 3, 4]


from app.routing.hill_climbing import local_search
from app.routing.tour import tour_cost as _tour_cost


def test_local_search_returns_local_optimum_no_worse_than_start():
    matrix = [
        [0, 2, 9, 10],
        [1, 0, 6, 4],
        [15, 7, 0, 8],
        [6, 3, 12, 0],
    ]
    start = [0, 1, 2, 3]
    start_cost = _tour_cost(matrix, start)
    visited: set[tuple[int, ...]] = set()
    best, best_cost = local_search(matrix, start, visited)
    assert best[0] == 0
    assert sorted(best) == [0, 1, 2, 3]
    assert best_cost <= start_cost  # local search never makes the tour worse


def test_local_search_is_monotonic_on_a_symmetric_instance():
    # Points on a line: 0,1,2,3 at x = 0,10,20,30 (symmetric distances).
    matrix = [
        [0, 10, 20, 30],
        [10, 0, 10, 20],
        [20, 10, 0, 10],
        [30, 20, 10, 0],
    ]
    visited: set[tuple[int, ...]] = set()
    best, best_cost = local_search(matrix, [0, 2, 1, 3], visited)
    # Optimal line tour visits in order: 0-1-2-3-0 = 10+10+10+30 = 60
    assert best_cost == 60


def test_no_tour_evaluated_twice(monkeypatch):
    import app.routing.hill_climbing as hc

    calls: list[tuple[int, ...]] = []
    real = hc.tour_cost

    def spy(matrix, tour):
        calls.append(tuple(tour))
        return real(matrix, tour)

    monkeypatch.setattr(hc, "tour_cost", spy)
    matrix = [
        [0, 2, 9, 10],
        [1, 0, 6, 4],
        [15, 7, 0, 8],
        [6, 3, 12, 0],
    ]
    visited: set[tuple[int, ...]] = set()
    hc.local_search(matrix, [0, 1, 2, 3], visited)
    assert len(calls) == len(set(calls)), "no identical tour evaluated twice in a run"
