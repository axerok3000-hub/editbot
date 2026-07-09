import json
import os
from pathlib import Path


class ConnectionStore:
    """Persists business_connection_id -> owner user_id on disk."""

    def __init__(self, path: str):
        self._path = Path(path)
        self._data: dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            with self._path.open(encoding="utf-8") as f:
                self._data = json.load(f)

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._path.with_suffix(".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f)
        os.replace(tmp_path, self._path)

    def set(self, business_connection_id: str, owner_user_id: int) -> None:
        self._data[business_connection_id] = owner_user_id
        self._save()

    def remove(self, business_connection_id: str) -> None:
        if self._data.pop(business_connection_id, None) is not None:
            self._save()

    def get_owner(self, business_connection_id: str) -> int | None:
        return self._data.get(business_connection_id)
