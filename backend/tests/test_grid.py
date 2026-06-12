import pytest

from app.maps.grid import Grid, GridError, cell_center, neighbors, parse_grid


def test_parse_grid_dims():
    g = parse_grid(["...", ".#.", "..."], cell_size=40)
    assert (g.rows, g.cols) == (3, 3)
    assert g.is_free((0, 0)) is True
    assert g.is_free((1, 1)) is False  # '#'


def test_parse_grid_rejects_ragged():
    with pytest.raises(GridError):
        parse_grid(["...", ".."])


def test_parse_grid_rejects_bad_chars():
    with pytest.raises(GridError):
        parse_grid(["..", "xX"])


def test_parse_grid_rejects_empty():
    with pytest.raises(GridError):
        parse_grid([])


def test_neighbors_are_free_and_4connected():
    g = parse_grid(["...", ".#.", "..."])
    assert sorted(neighbors(g, (0, 1))) == sorted([(0, 0), (0, 2)])  # (1,1) is blocked


def test_cell_center_is_pixel_center():
    g = parse_grid(["..", ".."], cell_size=40)
    assert cell_center(g, (0, 0)) == (20.0, 20.0)
    assert cell_center(g, (1, 1)) == (60.0, 60.0)
