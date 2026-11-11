"""Local-folder storage: same interface as Drive, used for tests and offline work."""
from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .base import RemoteFile, Storage


class LocalStorage(Storage):
    def __init__(self, root: Path, folders: dict | None = None):
        self.root = Path(root)
        # A folder key may be mapped to another sub-folder name (e.g. images and texts in one folder).
        self.folders = folders or {}

    def _dir(self, key: str) -> Path:
        name = self.folders.get(key) or key
        d = Path(name) if Path(name).is_absolute() else self.root / name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _remote(self, p: Path) -> RemoteFile:
        stat = p.stat()
        return RemoteFile(
            id=str(p.resolve()), name=p.name, md5=hashlib.md5(p.read_bytes()).hexdigest(),
            modified=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(), size=stat.st_size,
        )

    def list(self, folder_key: str) -> list[RemoteFile]:
        return [self._remote(p) for p in sorted(self._dir(folder_key).iterdir()) if p.is_file()]

    def download(self, file: RemoteFile) -> bytes:
        return Path(file.id).read_bytes()

    def upload_text(self, folder_key: str, name: str, text: str) -> str:
        dest = self._dir(folder_key) / name
        dest.write_text(text, encoding="utf-8")
        return str(dest.resolve())

    def put(self, folder_key: str, name: str, data: bytes, mime: str = "application/octet-stream") -> RemoteFile:
        dest = self._dir(folder_key) / name
        dest.write_bytes(data)
        return self._remote(dest)

    def copy_into(self, file: RemoteFile, folder_key: str, name: str | None = None) -> str:
        dest = self._dir(folder_key) / (name or file.name)
        if Path(file.id).resolve() != dest.resolve():
            shutil.copyfile(file.id, dest)
        return str(dest.resolve())
