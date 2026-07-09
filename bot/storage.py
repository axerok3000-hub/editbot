import json
import os
from pathlib import Path


class ConnectionStore:
    """Persists business_connection_id -> {owner_id, is_enabled} on disk."""

    def __init__(self, path: str):
        self._path = Path(path)
        self._data: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        with self._path.open(encoding="utf-8") as f:
            raw = json.load(f)
        # legacy format was {bcid: owner_id}; normalize to {bcid: {owner_id, is_enabled}}
        self._data = {
            bcid: value if isinstance(value, dict) else {"owner_id": value, "is_enabled": True}
            for bcid, value in raw.items()
        }

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f)
        os.replace(tmp_path, self._path)

    def set(self, business_connection_id: str, owner_user_id: int, is_enabled: bool = True) -> None:
        self._data[business_connection_id] = {"owner_id": owner_user_id, "is_enabled": is_enabled}
        self._save()

    def remove(self, business_connection_id: str) -> None:
        if self._data.pop(business_connection_id, None) is not None:
            self._save()

    def get_owner(self, business_connection_id: str) -> int | None:
        entry = self._data.get(business_connection_id)
        return entry["owner_id"] if entry else None

    def get_for_owner(self, owner_id: int) -> tuple[str, bool] | None:
        """Returns (business_connection_id, is_enabled) for the given owner, if any."""
        for bcid, entry in self._data.items():
            if entry["owner_id"] == owner_id:
                return bcid, entry["is_enabled"]
        return None


class ExcludedChatsStore:
    """Persists the set of chat_ids where the typewriter effect is disabled."""

    def __init__(self, path: str):
        self._path = Path(path)
        self._chat_ids: set[int] = set()
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            with self._path.open(encoding="utf-8") as f:
                self._chat_ids = set(json.load(f))

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(sorted(self._chat_ids), f)
        os.replace(tmp_path, self._path)

    def exclude(self, chat_id: int) -> None:
        if chat_id not in self._chat_ids:
            self._chat_ids.add(chat_id)
            self._save()

    def include(self, chat_id: int) -> None:
        if chat_id in self._chat_ids:
            self._chat_ids.discard(chat_id)
            self._save()

    def is_excluded(self, chat_id: int) -> bool:
        return chat_id in self._chat_ids

    def all(self) -> list[int]:
        return sorted(self._chat_ids)
