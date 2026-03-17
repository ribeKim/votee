from __future__ import annotations

from datetime import UTC
from datetime import datetime
from datetime import timedelta
import hashlib
import re
import secrets


def now_utc() -> datetime:
    return datetime.now(UTC)


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def slugify(value: str) -> str:
    lowered = value.lower().strip()
    compact = re.sub(r"[^a-z0-9]+", "-", lowered)
    stripped = compact.strip("-")
    return stripped or "votee-user"


def session_expiry(days: int = 14) -> datetime:
    return now_utc() + timedelta(days=days)


def build_discord_avatar_url(discord_id: str, avatar_hash: str | None) -> str | None:
    if avatar_hash is None:
        return None
    return f"https://cdn.discordapp.com/avatars/{discord_id}/{avatar_hash}.png"
