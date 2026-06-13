"""SQLite persistence for optimization runs.

Each row is a self-contained snapshot: enough to re-render both charts even if
the source map is later deleted. Structured fields are stored JSON-encoded.
A connection is opened per operation; the schema is created on first use.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from app.config import get_settings


class RunError(Exception):
    """Base class for run-store errors."""


class RunNotFound(RunError):
    """Raised when a run id does not exist."""


_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    map_id TEXT NOT NULL,
    map_name TEXT NOT NULL,
    start_id TEXT NOT NULL,
    restarts INTEGER NOT NULL,
    seed INTEGER,
    total_cost REAL NOT NULL,
    random_cost REAL NOT NULL,
    brute_force_cost REAL,
    stop_order TEXT NOT NULL,
    stop_labels TEXT NOT NULL,
    tour TEXT NOT NULL,
    matrix TEXT NOT NULL,
    full_history TEXT NOT NULL,
    restart_indices TEXT NOT NULL,
    grid_snapshot TEXT NOT NULL
)
"""


def _connect() -> sqlite3.Connection:
    path = get_settings().runs_db
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    return conn


def record_run(
    *, map_id, map_name, start_id, restarts, seed, total_cost, random_cost,
    brute_force_cost, stop_order, stop_labels, tour, matrix, full_history,
    restart_indices, grid_snapshot,
) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        cur = conn.execute(
            """INSERT INTO runs (created_at, map_id, map_name, start_id, restarts,
               seed, total_cost, random_cost, brute_force_cost, stop_order,
               stop_labels, tour, matrix, full_history, restart_indices,
               grid_snapshot)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                created_at, map_id, map_name, start_id, restarts, seed,
                total_cost, random_cost, brute_force_cost,
                json.dumps(stop_order), json.dumps(stop_labels), json.dumps(tour),
                json.dumps(matrix), json.dumps(full_history),
                json.dumps(restart_indices), json.dumps(grid_snapshot),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def _row_to_run(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "map_id": row["map_id"],
        "map_name": row["map_name"],
        "start_id": row["start_id"],
        "restarts": row["restarts"],
        "seed": row["seed"],
        "total_cost": row["total_cost"],
        "random_cost": row["random_cost"],
        "brute_force_cost": row["brute_force_cost"],
        "stop_order": json.loads(row["stop_order"]),
        "stop_labels": json.loads(row["stop_labels"]),
        "tour": json.loads(row["tour"]),
        "matrix": json.loads(row["matrix"]),
        "full_history": json.loads(row["full_history"]),
        "restart_indices": json.loads(row["restart_indices"]),
        "grid_snapshot": json.loads(row["grid_snapshot"]),
    }


def get_run(run_id: int) -> dict:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise RunNotFound(f"run {run_id} not found")
    return _row_to_run(row)


def list_runs() -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT id, created_at, map_id, map_name, total_cost, stop_order
               FROM runs ORDER BY id DESC"""
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "id": r["id"],
            "created_at": r["created_at"],
            "map_id": r["map_id"],
            "map_name": r["map_name"],
            "total_cost": r["total_cost"],
            "stop_count": len(json.loads(r["stop_order"])),
        }
        for r in rows
    ]


def delete_run(run_id: int) -> None:
    conn = _connect()
    try:
        cur = conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        conn.commit()
        deleted = cur.rowcount
    finally:
        conn.close()
    if deleted == 0:
        raise RunNotFound(f"run {run_id} not found")
