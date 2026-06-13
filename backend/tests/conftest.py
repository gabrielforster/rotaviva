import pytest


@pytest.fixture
def temp_store(tmp_path, monkeypatch):
    """Point the map store at empty temp preset/data dirs via env vars.

    Returns (presets_dir, data_dir) as Paths. Because Settings reads env on
    every call (no caching), this isolates each test's filesystem.
    """
    presets = tmp_path / "presets"
    presets.mkdir()
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("ROTAVIVA_PRESETS_DIR", str(presets))
    monkeypatch.setenv("ROTAVIVA_DATA_DIR", str(data))
    monkeypatch.setenv("ROTAVIVA_RUNS_DB", str(data / "runs.db"))
    return presets, data
