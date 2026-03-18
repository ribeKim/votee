from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import uuid

from app.config import Settings


@dataclass
class StoredObject:
    object_key: str
    public_url: str


class StorageService(Protocol):
    async def upload_avatar(self, owner_id: str, content_type: str, payload: bytes) -> StoredObject:
        ...


class LocalStorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.upload_root = Path(__file__).resolve().parents[2] / "uploads"
        self.upload_root.mkdir(parents=True, exist_ok=True)

    async def upload_avatar(self, owner_id: str, content_type: str, payload: bytes) -> StoredObject:
        extension = _extension_for_mime(content_type)
        object_key = f"{owner_id}/{uuid.uuid4()}.{extension}"
        target = self.upload_root / object_key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return StoredObject(object_key=object_key, public_url=f"{self.settings.storage_public_url.rstrip('/')}/{object_key}")


def _extension_for_mime(content_type: str) -> str:
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    return mapping.get(content_type, "bin")
