"""Storage interface: the pipeline never talks to Google Drive directly, only to this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
GOOGLE_DOC = "application/vnd.google-apps.document"


@dataclass(frozen=True)
class RemoteFile:
    id: str
    name: str
    mime: str = ""
    md5: str | None = None
    modified: str | None = None
    size: int | None = None

    @property
    def stem(self) -> str:
        return Path(self.name).stem if self.suffix else self.name

    @property
    def suffix(self) -> str:
        return Path(self.name).suffix.lower()

    @property
    def is_image(self) -> bool:
        return self.suffix in IMAGE_EXT or self.mime.startswith("image/")

    @property
    def is_text(self) -> bool:
        return self.suffix == ".txt" or self.mime == GOOGLE_DOC

    @property
    def version(self) -> str:
        """Changes whenever the file content changes (Google Docs have no md5)."""
        return self.md5 or self.modified or ""


class Storage(ABC):
    """Folder keys: train_images, train_texts, inbox, output (see config.yaml)."""

    @abstractmethod
    def list(self, folder_key: str) -> list[RemoteFile]: ...

    @abstractmethod
    def download(self, file: RemoteFile) -> bytes: ...

    @abstractmethod
    def upload_text(self, folder_key: str, name: str, text: str) -> str:
        """Create or overwrite a UTF-8 text file; return its id."""

    @abstractmethod
    def copy_into(self, file: RemoteFile, folder_key: str, name: str | None = None) -> str:
        """Copy an existing file into another folder; return the new id."""

    @abstractmethod
    def put(self, folder_key: str, name: str, data: bytes, mime: str = "application/octet-stream") -> RemoteFile:
        """Create or overwrite a file from bytes; return it with its version (md5/modified)."""
