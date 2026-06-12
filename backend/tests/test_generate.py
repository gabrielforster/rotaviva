import math

import pytest

from app.maps.generate import generate_map
from app.maps.store import validate_map


def test_generate_shape_and_validity():
    m = generate_map("gen-x", "Gerado X", n=5, seed=1)
    assert m["id"] == "gen-x"
    assert m["name"] == "Gerado X"
    assert m["source"] == "generated"
    assert len(m["points"]) == 5
    assert len(m["matrix"]) == 5 and all(len(row) == 5 for row in m["matrix"])
    # A generated map must pass the store's structural validation.
    validate_map(m)


def test_generate_is_deterministic_for_a_seed():
    assert generate_map("g", "G", n=6, seed=42) == generate_map("g", "G", n=6, seed=42)


def test_generated_matrix_is_euclidean_and_symmetric():
    m = generate_map("g", "G", n=4, seed=7)
    pts = [(p["x"], p["y"]) for p in m["points"]]
    for i in range(4):
        for j in range(4):
            expected = round(math.dist(pts[i], pts[j]), 2)
            assert m["matrix"][i][j] == pytest.approx(expected)
            assert m["matrix"][i][j] == pytest.approx(m["matrix"][j][i])
    assert m["matrix"][0][0] == 0
