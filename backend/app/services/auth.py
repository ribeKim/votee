from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.config import Settings
from app.security import build_discord_avatar_url


@dataclass
class DiscordIdentity:
    discord_id: str
    username: str
    display_name: str
    avatar_url: str | None


class DiscordOAuthService(Protocol):
    async def build_authorization_url(self, state: str) -> str:
        ...

    async def exchange_code(self, code: str) -> DiscordIdentity:
        ...


class AuthlibDiscordOAuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def build_authorization_url(self, state: str) -> str:
        async with AsyncOAuth2Client(
            client_id=self.settings.discord_client_id,
            client_secret=self.settings.discord_client_secret,
            redirect_uri=self.settings.discord_redirect_uri,
            scope="identify",
            token_endpoint_auth_method="client_secret_post",
        ) as client:
            url, _ = client.create_authorization_url(
                "https://discord.com/oauth2/authorize",
                state=state,
            )
            return url

    async def exchange_code(self, code: str) -> DiscordIdentity:
        async with AsyncOAuth2Client(
            client_id=self.settings.discord_client_id,
            client_secret=self.settings.discord_client_secret,
            redirect_uri=self.settings.discord_redirect_uri,
            scope="identify",
            token_endpoint_auth_method="client_secret_post",
        ) as client:
            token = await client.fetch_token(
                "https://discord.com/api/oauth2/token",
                code=code,
                grant_type="authorization_code",
            )
            access_token = token.get("access_token")
            if not access_token:
                raise ValueError("Discord OAuth token response did not include an access token.")
            response = await client.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            payload = response.json()
            return DiscordIdentity(
                discord_id=str(payload["id"]),
                username=payload["username"],
                display_name=payload.get("global_name") or payload["username"],
                avatar_url=build_discord_avatar_url(str(payload["id"]), payload.get("avatar")),
            )
