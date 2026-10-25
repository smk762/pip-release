"""SQLite queue of seen versions and drafts."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from pip_release.models import DRAFT_FIELDS, Draft

_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    name TEXT PRIMARY KEY,
    baselined_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS seen (
    project TEXT NOT NULL,
    version TEXT NOT NULL,
    seen_at TEXT NOT NULL,
    PRIMARY KEY (project, version)
);
CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project TEXT NOT NULL,
    version TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    link TEXT NOT NULL,
    status TEXT NOT NULL,
    edited INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    note TEXT,
    external_id TEXT,
    error TEXT,
    UNIQUE (project, version, platform)
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Store:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(path, isolation_level=None, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript(_SCHEMA)

    def close(self) -> None:
        self.conn.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        self.conn.execute("BEGIN")
        try:
            yield
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def is_baselined(self, project: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM projects WHERE name = ?", (project,)
        ).fetchone()
        return row is not None

    def baseline(self, project: str, versions: list[str]) -> None:
        now = _now()
        with self.transaction():
            self.conn.execute(
                "INSERT OR IGNORE INTO projects (name, baselined_at) VALUES (?, ?)",
                (project, now),
            )
            self.conn.executemany(
                "INSERT OR IGNORE INTO seen (project, version, seen_at) VALUES (?, ?, ?)",
                [(project, version, now) for version in versions],
            )

    def seen(self, project: str, version: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM seen WHERE project = ? AND version = ?",
            (project, version),
        ).fetchone()
        return row is not None

    def mark_seen(self, project: str, version: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO seen (project, version, seen_at) VALUES (?, ?, ?)",
            (project, version, _now()),
        )
        self.conn.commit()

    def add_draft(
        self,
        *,
        project: str,
        version: str,
        platform: str,
        title: str,
        body: str,
        link: str,
    ) -> tuple[int, bool]:
        now = _now()
        cur = self.conn.execute(
            """
            INSERT OR IGNORE INTO drafts (
                project, version, platform, title, body, link, status,
                edited, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?, ?)
            """,
            (project, version, platform, title, body, link, now, now),
        )
        self.conn.commit()
        if cur.rowcount:
            return int(cur.lastrowid), True
        row = self.conn.execute(
            "SELECT id FROM drafts WHERE project = ? AND version = ? AND platform = ?",
            (project, version, platform),
        ).fetchone()
        return int(row["id"]), False

    def get(self, draft_id: int) -> Draft | None:
        row = self.conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        return _draft(row) if row else None

    def list_drafts(
        self,
        *,
        status: str | None = None,
        project: str | None = None,
        version: str | None = None,
    ) -> list[Draft]:
        clauses: list[str] = []
        params: list[object] = []
        if status:
            clauses.append("status = ?")
            params.append(status)
        if project:
            clauses.append("project = ?")
            params.append(project)
        if version:
            clauses.append("version = ?")
            params.append(version)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.conn.execute(
            f"SELECT * FROM drafts {where} ORDER BY id", params
        ).fetchall()
        return [_draft(row) for row in rows]

    def transition(
        self,
        draft_id: int,
        from_statuses: tuple[str, ...],
        to_status: str,
        **fields: object,
    ) -> Draft | None:
        assignments = ["status = ?", "updated_at = ?"]
        params: list[object] = [to_status, _now()]
        for key, value in fields.items():
            if key not in DRAFT_FIELDS:
                raise ValueError(f"Unknown draft field {key}")
            assignments.append(f"{key} = ?")
            params.append(value)
        marks = ", ".join("?" for _ in from_statuses)
        params.extend([draft_id, *from_statuses])
        cur = self.conn.execute(
            f"""
            UPDATE drafts SET {", ".join(assignments)}
            WHERE id = ? AND status IN ({marks})
            """,
            params,
        )
        self.conn.commit()
        if cur.rowcount != 1:
            return None
        return self.get(draft_id)

    def update_text(
        self, draft_id: int, title: str, body: str, from_statuses: tuple[str, ...]
    ) -> Draft | None:
        return self.transition(
            draft_id,
            from_statuses,
            "pending",
            title=title,
            body=body,
            edited=1,
            error=None,
        )


def _draft(row: sqlite3.Row) -> Draft:
    return Draft(
        id=int(row["id"]),
        project=row["project"],
        version=row["version"],
        platform=row["platform"],
        title=row["title"],
        body=row["body"],
        link=row["link"],
        status=row["status"],
        edited=bool(row["edited"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        note=row["note"],
        external_id=row["external_id"],
        error=row["error"],
    )
