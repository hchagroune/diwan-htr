"""SQLite job queue shared by the pipeline (writer) and the review dashboard (reader/editor)."""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

STATUSES = ("pending", "needs_review", "approved", "exported", "verified", "rejected", "error")
JSON_COLS = ("flags", "line_scores", "critic", "examples", "usage")

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id TEXT PRIMARY KEY,           -- storage file id of the source image
  name TEXT NOT NULL,            -- e.g. FRANOM88_1MIOM31_0201.jpg
  kind TEXT DEFAULT 'inbox',     -- inbox = new page | training = ground-truth check of a training pair
  source_version TEXT,
  image_path TEXT,               -- local preprocessed copy shown in the dashboard
  status TEXT NOT NULL DEFAULT 'pending',
  draft TEXT,                    -- machine transcription
  final TEXT,                    -- human-validated transcription
  confidence REAL,
  flags TEXT, line_scores TEXT, critic TEXT, examples TEXT, usage TEXT,
  model TEXT,
  attempts INTEGER DEFAULT 0,
  reviewer TEXT,
  review_cer REAL,               -- how much the reviewer changed the draft (model quality signal)
  output_id TEXT,
  in_training INTEGER DEFAULT 0,
  note TEXT,
  error TEXT,
  created_at TEXT, updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class JobStore:
    def __init__(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()  # the web server calls the store from several threads
        self.conn = sqlite3.connect(str(path), check_same_thread=False, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")  # pipeline and dashboard can run at the same time
        self.conn.executescript(SCHEMA)

    def _row(self, row) -> dict | None:
        if row is None:
            return None
        d = dict(row)
        for col in JSON_COLS:
            d[col] = json.loads(d[col]) if d.get(col) else ([] if col in ("flags", "line_scores", "examples") else {})
        return d

    def get(self, job_id: str) -> dict | None:
        with self.lock:
            return self._row(self.conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone())

    def create(self, job_id: str, name: str, source_version: str = "", kind: str = "inbox",
               status: str = "pending") -> bool:
        with self.lock:
            cur = self.conn.execute(
                "INSERT OR IGNORE INTO jobs(id, name, kind, source_version, status, created_at, updated_at) "
                "VALUES (?,?,?,?,?,?,?)", (job_id, name, kind, source_version, status, _now(), _now()))
            self.conn.commit()
            return cur.rowcount > 0

    def update(self, job_id: str, **fields) -> None:
        for col in JSON_COLS:
            if col in fields and not isinstance(fields[col], str):
                fields[col] = json.dumps(fields[col], ensure_ascii=False)
        fields["updated_at"] = _now()
        cols = ", ".join(f"{k}=?" for k in fields)
        with self.lock:
            self.conn.execute(f"UPDATE jobs SET {cols} WHERE id=?", (*fields.values(), job_id))
            self.conn.commit()

    def delete(self, job_id: str) -> None:
        with self.lock:
            self.conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
            self.conn.commit()

    def export_rows(self) -> list[dict]:
        """All jobs as plain dicts (for backing the queue up to Drive)."""
        with self.lock:
            return [dict(r) for r in self.conn.execute("SELECT * FROM jobs").fetchall()]

    def import_rows(self, rows: list[dict]) -> int:
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(jobs)").fetchall()]
        n = 0
        with self.lock:
            for row in rows:
                data = {k: row.get(k) for k in cols if k in row}
                if not data.get("id"):
                    continue
                q = f"INSERT OR REPLACE INTO jobs({','.join(data)}) VALUES ({','.join('?' * len(data))})"
                self.conn.execute(q, tuple(data.values()))
                n += 1
            self.conn.commit()
        return n

    def list(self, statuses: list[str] | None = None, order: str = "confidence") -> list[dict]:
        order_sql = {"confidence": "COALESCE(confidence, 0) ASC, name", "name": "name",
                     "recent": "updated_at DESC"}.get(order, "name")
        with self.lock:
            if statuses:
                q = f"SELECT * FROM jobs WHERE status IN ({','.join('?' * len(statuses))}) ORDER BY {order_sql}"
                rows = self.conn.execute(q, statuses).fetchall()
            else:
                rows = self.conn.execute(f"SELECT * FROM jobs ORDER BY {order_sql}").fetchall()
            return [self._row(r) for r in rows]

    def stats(self) -> dict:
        with self.lock:
            counts = dict(self.conn.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall())
            row = self.conn.execute(
                "SELECT AVG(review_cer), COUNT(review_cer) FROM (SELECT review_cer FROM jobs "
                "WHERE review_cer IS NOT NULL ORDER BY updated_at DESC LIMIT 50)").fetchone()
        return {"counts": {s: counts.get(s, 0) for s in STATUSES},
                "recent_review_cer": row[0], "reviewed": row[1]}
