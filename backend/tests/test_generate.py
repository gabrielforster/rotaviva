import pytest

from app.maps.generate import SIZES, generate_map
from app.maps.grid import matrix_for_map, parse_grid, validate_points


@pytest.mark.parametrize("style", ["city", "warehouse"])
def test_generate_produces_valid_connected_map(style):
    m = generate_map("g1", "G1", 6, style=style, size="medium", density=0.6, seed=7)
    assert m["style"] == style
    assert m["source"] == "generated"
    assert "matrix" not in m
    grid = parse_grid(list(m["grid"]["cells"]), m["grid"]["cell_size"])
    cells = [(p["cell"]["row"], p["cell"]["col"]) for p in m["points"]]
    validate_points(grid, cells)  # in-bounds, free, distinct, connected -> no raise


@pytest.mark.parametrize("style", ["city", "warehouse"])
def test_generate_is_deterministic_for_seed(style):
    a = generate_map("g", "G", 5, style=style, seed=42)
    b = generate_map("g", "G", 5, style=style, seed=42)
    assert a == b


def test_generate_places_exactly_n_points():
    m = generate_map("g", "G", 4, style="city", size="small", seed=1)
    assert len(m["points"]) == 4
    ids = [p["id"] for p in m["points"]]
    assert len(set(ids)) == 4


def test_generate_unknown_style_raises():
    with pytest.raises(ValueError):
        generate_map("g", "G", 3, style="village", seed=1)


def test_generated_matrix_is_derivable():
    m = generate_map("g", "G", 5, style="warehouse", seed=3)
    matrix = matrix_for_map(m)
    assert len(matrix) == 5 and matrix[0][0] == 0
