import pytest

from app.runs import store as runs


def _sample() -> dict:
    return dict(
        map_id="centro", map_name="Centro", start_id="a", restarts=20, seed=7,
        total_cost=36.0, random_cost=42.0, brute_force_cost=36.0,
        stop_order=["a", "b", "c"], stop_labels=["A", "B", "C"],
        tour=["a", "b", "c", "a"], matrix=[[0, 3, 5], [3, 0, 4], [5, 4, 0]],
        full_history=[50.0, 40.0, 36.0], restart_indices=[0],
        grid_snapshot={"cell_size": 40, "cells": ["...", "..."], "points": []},
    )


def test_record_then_get_roundtrip(temp_store):
    run_id = runs.record_run(**_sample())
    assert isinstance(run_id, int) and run_id >= 1
    got = runs.get_run(run_id)
    assert got["id"] == run_id
    assert got["map_name"] == "Centro"
    assert got["tour"] == ["a", "b", "c", "a"]
    assert got["matrix"] == [[0, 3, 5], [3, 0, 4], [5, 4, 0]]
    assert got["full_history"] == [50.0, 40.0, 36.0]
    assert got["created_at"]  # non-empty ISO timestamp


def test_list_runs_newest_first_with_summary(temp_store):
    first = runs.record_run(**_sample())
    second = runs.record_run(**_sample())
    listed = runs.list_runs()
    assert [r["id"] for r in listed] == [second, first]
    assert listed[0]["stop_count"] == 3
    assert listed[0]["map_name"] == "Centro"


def test_get_missing_raises(temp_store):
    with pytest.raises(runs.RunNotFound):
        runs.get_run(999)


def test_delete_run(temp_store):
    run_id = runs.record_run(**_sample())
    runs.delete_run(run_id)
    with pytest.raises(runs.RunNotFound):
        runs.get_run(run_id)
    with pytest.raises(runs.RunNotFound):
        runs.delete_run(run_id)
