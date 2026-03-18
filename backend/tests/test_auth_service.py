from __future__ import annotations

from typing import Any

import pytest

from app.config import Settings
from app.services.auth import AuthlibDiscordOAuthService


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeAsyncOAuth2Client:
    last_headers: dict[str, str] | None = None

    def __init__(self, **_: Any) -> None:
        pass

    async def __aenter__(self) -> FakeAsyncOAuth2Client:
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    async def fetch_token(self, url: str, code: str, grant_type: str) -> dict[str, str]:
        assert url == "https://discord.com/api/oauth2/token"
        assert code == "oauth-code"
        assert grant_type == "authorization_code"
        return {"access_token": "discord-access-token"}

    async def get(self, url: str, headers: dict[str, str] | None = None) -> FakeResponse:
        assert url == "https://discord.com/api/users/@me"
        FakeAsyncOAuth2Client.last_headers = headers
        return FakeResponse(
            {
                "id": "123456",
                "username": "votee-user",
                "global_name": "Votee User",
                "avatar": "avatarhash",
            }
        )


@pytest.mark.anyio
async def test_exchange_code_uses_bearer_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.auth.AsyncOAuth2Client", FakeAsyncOAuth2Client)
    service = AuthlibDiscordOAuthService(
        Settings(
            discord_client_id="client-id",
            discord_client_secret="client-secret",
            discord_redirect_uri="http://localhost:8000/api/auth/discord/callback",
        )
    )

    identity = await service.exchange_code("oauth-code")

    assert FakeAsyncOAuth2Client.last_headers == {"Authorization": "Bearer discord-access-token"}
    assert identity.discord_id == "123456"
    assert identity.display_name == "Votee User"
    assert identity.avatar_url == "https://cdn.discordapp.com/avatars/123456/avatarhash.png"
