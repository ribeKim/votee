from __future__ import annotations

from datetime import UTC

from fastapi import Cookie
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.config import get_settings
from app.database import get_session
from app.models import Session as LoginSession
from app.models import User
from app.security import hash_token
from app.security import now_utc
from app.services.analysis import AnalysisService
from app.services.analysis import OpenAIAnalysisService
from app.services.analysis import TemplateAnalysisService
from app.services.auth import AuthlibDiscordOAuthService
from app.services.auth import DiscordOAuthService
from app.services.storage import LocalStorageService
from app.services.storage import StorageService
from app.services.storage import SupabaseStorageService


def get_app_settings() -> Settings:
    return get_settings()


def get_storage_service(settings: Settings = Depends(get_app_settings)) -> StorageService:
    if settings.storage_driver == "supabase" and settings.supabase_url and settings.supabase_service_role_key:
        return SupabaseStorageService(settings)
    return LocalStorageService(settings)


def get_analysis_service(settings: Settings = Depends(get_app_settings)) -> AnalysisService:
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return OpenAIAnalysisService(settings)
    return TemplateAnalysisService()


def get_discord_oauth_service(settings: Settings = Depends(get_app_settings)) -> DiscordOAuthService:
    return AuthlibDiscordOAuthService(settings)


def get_current_user(
    request: Request,
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_app_settings),
    legacy_cookie: str | None = Cookie(default=None, alias="votee_session"),
) -> User:
    effective_token = request.cookies.get(settings.session_cookie_name) or legacy_cookie
    if effective_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    hashed = hash_token(effective_token)
    login_session = session.scalar(select(LoginSession).where(LoginSession.token_hash == hashed))
    if login_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")
    expires_at = login_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now_utc():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")
    user = session.scalar(select(User).where(User.id == login_session.user_id))
    if user is None or user.is_suspended:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account unavailable.")
    login_session.last_seen_at = now_utc()
    session.commit()
    session.refresh(user)
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user
