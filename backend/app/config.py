from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="VOTEE_", extra="ignore")

    database_url: str = Field(default="postgresql+psycopg://votee:votee@db:5432/votee")
    redis_url: str = Field(default="redis://redis:6379/0")
    session_secret: str = Field(default="change-me")
    cookie_secure: bool = Field(default=False)
    session_cookie_name: str = Field(default="votee_session")
    frontend_url: str = Field(default="http://localhost:4173")
    public_app_url: str = Field(default="http://localhost:4173")
    api_base_url: str = Field(default="http://localhost:8000")
    discord_client_id: str = Field(default="")
    discord_client_secret: str = Field(default="")
    discord_redirect_uri: str = Field(default="http://localhost:8000/api/auth/discord/callback")
    discord_admin_ids: str = Field(default="")
    storage_public_url: str = Field(default="http://localhost:8000/uploads")
    ai_provider: str = Field(default="template")
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4.1-mini")
    max_upload_bytes: int = Field(default=5 * 1024 * 1024)
    allowed_image_types: str = Field(default="image/png,image/jpeg,image/webp")

    @property
    def admin_id_set(self) -> set[str]:
        return {value.strip() for value in self.discord_admin_ids.split(",") if value.strip()}

    @property
    def allowed_image_type_set(self) -> set[str]:
        return {value.strip() for value in self.allowed_image_types.split(",") if value.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
