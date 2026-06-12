from app.routing.tour import tour_cost


def test_known_tour_known_matrix():
    # 3 points; matrix[i][j] = distance i -> j (symmetric here)
    matrix = [
        [0, 12, 9],
        [12, 0, 5],
        [9, 5, 0],
    ]
    # Tour 0 -> 1 -> 2 -> back to 0 = 12 + 5 + 9 = 26
    assert tour_cost(matrix, [0, 1, 2]) == 26


def test_single_stop_costs_zero():
    assert tour_cost([[0]], [0]) == 0


def test_two_stops_round_trip():
    matrix = [[0, 7], [7, 0]]
    # 0 -> 1 -> back to 0 = 7 + 7 = 14
    assert tour_cost(matrix, [0, 1]) == 14


def test_asymmetric_matrix_uses_directed_edges():
    # Going 0->1 costs 1, returning 1->0 costs 100
    matrix = [
        [0, 1, 50],
        [100, 0, 2],
        [3, 4, 0],
    ]
    # 0 -> 1 -> 2 -> 0 = 1 + 2 + 3 = 6
    assert tour_cost(matrix, [0, 1, 2]) == 6
    # 0 -> 2 -> 1 -> 0 = 50 + 4 + 100 = 154
    assert tour_cost(matrix, [0, 2, 1]) == 154
