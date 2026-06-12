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


from app.maps.grid import bfs_distances, derive_matrix, matrix_for_map, validate_points


def test_bfs_routes_around_walls():
    # straight line is 2 cells, but a wall forces the path around -> 4 steps
    g = parse_grid([
        "...",
        "#.#",
        "...",
    ])
    # from (0,0) to (2,0): down is blocked at (1,0); must go right/down/left
    dist = bfs_distances(g, (0, 0))
    assert dist[(2, 0)] == 4


def test_derive_matrix_symmetric_with_known_values():
    g = parse_grid(["...", "...", "..."])  # open 3x3
    cells = [(0, 0), (0, 2), (2, 2)]
    m = derive_matrix(g, cells)
    assert m[0][0] == 0
    assert m[0][1] == 2 and m[1][0] == 2          # along the top row
    assert m[0][2] == 4 and m[2][0] == 4          # Manhattan corner-to-corner
    assert all(m[i][j] == m[j][i] for i in range(3) for j in range(3))  # symmetric


def test_validate_points_rejects_blocked_cell():
    g = parse_grid(["...", ".#.", "..."])
    with pytest.raises(GridError):
        validate_points(g, [(0, 0), (1, 1)])  # (1,1) is a wall


def test_validate_points_rejects_disconnected():
    g = parse_grid([
        "..#..",
        "..#..",
        "..#..",
    ])  # left half and right half split by a wall column
    with pytest.raises(GridError):
        validate_points(g, [(0, 0), (0, 4)])


def test_validate_points_rejects_duplicate_and_oob():
    g = parse_grid(["..", ".."])
    with pytest.raises(GridError):
        validate_points(g, [(0, 0), (0, 0)])
    with pytest.raises(GridError):
        validate_points(g, [(0, 0), (5, 5)])


def test_matrix_for_map_reads_point_cells():
    data = {
        "grid": {"cell_size": 40, "cells": ["...", "...", "..."]},
        "points": [
            {"id": "a", "cell": {"row": 0, "col": 0}},
            {"id": "b", "cell": {"row": 0, "col": 2}},
        ],
    }
    assert matrix_for_map(data) == [[0, 2], [2, 0]]
