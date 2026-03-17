from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
import uuid

import httpx

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


class SupabaseStorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def upload_avatar(self, owner_id: str, content_type: str, payload: bytes) -> StoredObject:
        extension = _extension_for_mime(content_type)
        object_key = f"{owner_id}/{uuid.uuid4()}.{extension}"
        url = f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/{self.settings.storage_bucket}/{object_key}"
        headers = {
            "Authorization": f"Bearer {self.settings.supabase_service_role_key}",
            "apikey": self.settings.supabase_service_role_key,
            "Content-Type": content_type,
            "x-upsert": "false",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, content=payload)
            response.raise_for_status()
        public_url = f"{self.settings.supabase_url.rstrip('/')}/storage/v1/object/public/{self.settings.storage_bucket}/{object_key}"
        return StoredObject(object_key=object_key, public_url=public_url)


def _extension_for_mime(content_type: str) -> str:
    mapping = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    return mapping.get(content_type, "bin")

