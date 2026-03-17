from __future__ import annotations

from datetime import timedelta
import secrets

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from fastapi import status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_session
from app.dependencies import get_app_settings
from app.dependencies import get_current_user
from app.dependencies import get_discord_oauth_service
from app.models import Avatar
from app.models import Session as LoginSession
from app.models import User
from app.schemas import AuthenticatedUserResponse
from app.schemas import AvatarSummary
from app.schemas import UserSummary
from app.security import create_session_token
from app.security import hash_token
from app.security import now_utc
from app.security import session_expiry
from app.security import slugify
from app.services.auth import DiscordIdentity
from app.services.auth import DiscordOAuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _serialize_user(user: User, avatars: list[Avatar]) -> AuthenticatedUserResponse:
    return AuthenticatedUserResponse(
        user=UserSummary(
            id=user.id,
            display_name=user.display_name,
            username=user.username,
            slug=user.slug,
            avatar_url=user.avatar_url,
            bio=user.bio,
            is_admin=user.is_admin,
        ),
        avatars=[
            AvatarSummary(
                id=avatar.id,
                title=avatar.title,
                description=avatar.description,
                image_url=avatar.image_url,
                status=avatar.status,
                is_primary=avatar.is_primary,
                elo_rating=avatar.elo_rating,
                wins=avatar.wins,
                losses=avatar.losses,
                width=avatar.width,
                height=avatar.height,
                created_at=avatar.created_at,
            )
            for avatar in avatars
        ],
    )


def _ensure_unique_slug(session: Session, base_slug: str, discord_id: str) -> str:
    candidate = base_slug
    counter = 1
    while session.scalar(select(User).where(User.slug == candidate, User.discord_id != discord_id)) is not None:
        candidate = f"{base_slug}-{counter}"
        counter += 1
    return candidate


def _upsert_user(session: Session, settings: Settings, identity: DiscordIdentity) -> User:
    user = session.scalar(select(User).where(User.discord_id == identity.discord_id))
    slug = _ensure_unique_slug(session, slugify(identity.display_name), identity.discord_id)
    if user is None:
        user = User(
            discord_id=identity.discord_id,
            username=identity.username,
            display_name=identity.display_name,
            avatar_url=identity.avatar_url,
            slug=slug,
            is_admin=identity.discord_id in settings.admin_id_set,
        )
        session.add(user)
    else:
        user.username = identity.username
        user.display_name = identity.display_name
        user.avatar_url = identity.avatar_url
        user.slug = slug
        user.is_admin = identity.discord_id in settings.admin_id_set or user.is_admin
    session.commit()
    session.refresh(user)
    return user


@router.get("/discord/login")
async def discord_login(
    oauth_service: DiscordOAuthService = Depends(get_discord_oauth_service),
) -> Response:
    state = secrets.token_urlsafe(24)
    authorization_url = await oauth_service.build_authorization_url(state)
    redirect = RedirectResponse(url=authorization_url, status_code=status.HTTP_302_FOUND)
    redirect.set_cookie("votee_oauth_state", state, httponly=True, max_age=600, samesite="lax")
    return redirect


@router.get("/discord/callback")
async def discord_callback(
    request: Request,
    code: str,
    state: str,
    oauth_service: DiscordOAuthService = Depends(get_discord_oauth_service),
    settings: Settings = Depends(get_app_settings),
    session: Session = Depends(get_session),
) -> Response:
    stored_state = request.cookies.get("votee_oauth_state")
    if stored_state is None or stored_state != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state.")
    identity = await oauth_service.exchange_code(code)
    user = _upsert_user(session, settings, identity)
    token = create_session_token()
    login_session = LoginSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=session_expiry(),
        last_seen_at=now_utc(),
    )
    session.add(login_session)
    session.commit()
    redirect = RedirectResponse(url=f"{settings.frontend_url.rstrip('/')}/feed", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie("votee_oauth_state")
    redirect.set_cookie(
        settings.session_cookie_name,
        token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=int(timedelta(days=14).total_seconds()),
        path="/",
    )
    return redirect


@router.get("/me", response_model=AuthenticatedUserResponse)
def current_user(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AuthenticatedUserResponse:
    avatars = list(session.scalars(select(Avatar).where(Avatar.owner_id == user.id).order_by(Avatar.created_at.desc())))
    return _serialize_user(user, avatars)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    settings: Settings = Depends(get_app_settings),
    session: Session = Depends(get_session),
) -> Response:
    session_token = request.cookies.get(settings.session_cookie_name)
    if session_token is not None:
        login_session = session.scalar(select(LoginSession).where(LoginSession.token_hash == hash_token(session_token)))
        if login_session is not None:
            session.delete(login_session)
            session.commit()
    response.delete_cookie(settings.session_cookie_name, path="/")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

