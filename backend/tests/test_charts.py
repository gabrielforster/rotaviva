from app.charts import evolution_png, route_png

_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def test_route_png_returns_png_bytes():
    cells = ["....", ".##.", "...."]
    points = [
        {"id": "a", "label": "A", "cell": {"row": 0, "col": 0}},
        {"id": "b", "label": "B", "cell": {"row": 2, "col": 3}},
    ]
    tour = ["a", "b", "a"]
    png = route_png(cells, 40, points, tour, total_cost=8.0)
    assert isinstance(png, bytes) and png.startswith(_PNG_MAGIC) and len(png) > 100


def test_evolution_png_returns_png_bytes():
    full_history = [50.0, 40.0, 38.0, 60.0, 45.0, 30.0]
    restart_indices = [0, 3]
    png = evolution_png(full_history, restart_indices, best_cost=30.0)
    assert isinstance(png, bytes) and png.startswith(_PNG_MAGIC) and len(png) > 100
