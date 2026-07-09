import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CachedMessage:
    chat_id: int
    message_id: int
    sender_id: int | None
    sender_name: str | None
    text: str | None
    media_type: str | None
    file_id: str | None
    created_at: int
    deleted_at: int | None


class MessageCache:
    """SQLite-backed cache of business messages, used for anti-deletion tracking."""

    def __init__(self, path: str):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cached (
                    chat_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    sender_id INTEGER,
                    sender_name TEXT,
                    text TEXT,
                    media_type TEXT,
                    file_id TEXT,
                    created_at INTEGER NOT NULL,
                    deleted_at INTEGER,
                    PRIMARY KEY (chat_id, message_id)
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def save(
        self,
        chat_id: int,
        message_id: int,
        sender_id: int | None,
        sender_name: str | None,
        text: str | None,
        media_type: str | None,
        file_id: str | None,
        created_at: int | None = None,
    ) -> None:
        created_at = created_at if created_at is not None else int(time.time())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cached
                    (chat_id, message_id, sender_id, sender_name, text, media_type, file_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(chat_id, message_id) DO UPDATE SET
                    sender_id = excluded.sender_id,
                    sender_name = excluded.sender_name,
                    text = excluded.text,
                    media_type = excluded.media_type,
                    file_id = excluded.file_id
                """,
                (chat_id, message_id, sender_id, sender_name, text, media_type, file_id, created_at),
            )

    def get(self, chat_id: int, message_id: int) -> CachedMessage | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM cached WHERE chat_id = ? AND message_id = ?",
                (chat_id, message_id),
            ).fetchone()
        return CachedMessage(**dict(row)) if row else None

    def mark_deleted(self, chat_id: int, message_id: int, deleted_at: int | None = None) -> None:
        deleted_at = deleted_at if deleted_at is not None else int(time.time())
        with self._connect() as conn:
            conn.execute(
                "UPDATE cached SET deleted_at = ? WHERE chat_id = ? AND message_id = ?",
                (deleted_at, chat_id, message_id),
            )

    def recent_deleted(self, limit: int = 10) -> list[CachedMessage]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM cached WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [CachedMessage(**dict(row)) for row in rows]

    def purge_older_than(self, cutoff_timestamp: int) -> int:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM cached WHERE created_at < ?", (cutoff_timestamp,))
            return cur.rowcount


class SettingsStore:
    """SQLite-backed per-owner settings, e.g. the chosen text style."""

    DEFAULT_STYLE = "normal"

    def __init__(self, path: str):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    owner_id INTEGER PRIMARY KEY,
                    style TEXT NOT NULL DEFAULT 'normal'
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_style(self, owner_id: int) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT style FROM settings WHERE owner_id = ?", (owner_id,)
            ).fetchone()
        return row["style"] if row else self.DEFAULT_STYLE

    def set_style(self, owner_id: int, style: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO settings (owner_id, style) VALUES (?, ?)
                ON CONFLICT(owner_id) DO UPDATE SET style = excluded.style
                """,
                (owner_id, style),
            )
