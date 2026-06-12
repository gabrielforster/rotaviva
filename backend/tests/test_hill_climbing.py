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
