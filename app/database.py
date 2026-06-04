"""SQLite helpers for local audit persistence."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.getenv("MB8_DB_PATH", str(Path(__file__).resolve().parents[1] / "mb8_adaptive_stoic.sqlite3")))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                audit_trail_id TEXT PRIMARY KEY,
                match TEXT NOT NULL,
                final_decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                audit_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS run_history (
                run_id TEXT PRIMARY KEY,
                source_filename TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                final_count INTEGER NOT NULL,
                rejected_count INTEGER NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_audit_log(audit_trail_id: str, match: str, final_decision: str, reason: str, audit_json: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO audit_logs
                (audit_trail_id, match, final_decision, reason, audit_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (audit_trail_id, match, final_decision, reason, audit_json),
        )


def save_run_history(
    run_id: str,
    source_filename: str,
    total_rows: int,
    final_count: int,
    rejected_count: int,
    result: dict[str, Any],
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO run_history
                (run_id, source_filename, total_rows, final_count, rejected_count, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                source_filename,
                total_rows,
                final_count,
                rejected_count,
                json.dumps(result),
            ),
        )


def list_run_history(limit: int = 25) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT run_id, source_filename, total_rows, final_count, rejected_count, created_at
            FROM run_history
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_run_history(run_id: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT run_id, source_filename, total_rows, final_count, rejected_count, result_json, created_at
            FROM run_history
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["result"] = json.loads(str(data.pop("result_json")))
    return data
