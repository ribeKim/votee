from __future__ import annotations

from collections.abc import Generator
from io import BytesIO
import os

os.environ.setdefault("VOTEE_DATABASE_URL", "sqlite:///./test-import.db")
os.environ.setdefault("VOTEE_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("VOTEE_FRONTEND_URL", "http://testserver")
os.environ.setdefault("VOTEE_PUBLIC_APP_URL", "http://testserver")

from fastapi.testclient import TestClient
from PIL import Image
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.database import Base
from app.dependencies import get_analysis_service
from app.dependencies import get_app_settings
from app.dependencies import get_discord_oauth_service
from app.dependencies import get_session
from app.dependencies import get_storage_service
from app.main import app
from app.models import Avatar
from app.models import Session as LoginSession
from app.models import User
from app.security import create_session_token
from app.security import hash_token
from app.security import session_expiry
from app.services.analysis import TemplateAnalysisService
from app.services.auth import DiscordIdentity


class FakeDiscordOAuthService:
    async def build_authorization_url(self, state: str) -> str:
        return f"https://discord.example.test/oauth?state={state}"

    async def exchange_code(self, code: str) -> DiscordIdentity:
        suffix = code[-4:]
        return DiscordIdentity(
            discord_id=f"discord-{suffix}",
            username=f"user-{suffix}",
            display_name=f"User {suffix}",
            avatar_url=f"https://cdn.example.test/{suffix}.png",
        )


class FakeStorageService:
    async def upload_avatar(self, owner_id: str, content_type: str, payload: bytes):
        return type("StoredObject", (), {"object_key": f"{owner_id}/avatar.png", "public_url": f"http://testserver/uploads/{owner_id}/avatar.png"})()


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        database_url="sqlite:///./backend/data/test.db",
        frontend_url="http://testserver",
        public_app_url="http://testserver",
        storage_driver="local",
        storage_public_url="http://testserver/uploads",
        discord_admin_ids="discord-admin",
    )


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        future=True,
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    Base.metadata.create_all(engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session, settings: Settings) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_app_settings] = lambda: settings
    app.dependency_overrides[get_discord_oauth_service] = lambda: FakeDiscordOAuthService()
    app.dependency_overrides[get_storage_service] = lambda: FakeStorageService()
    app.dependency_overrides[get_analysis_service] = lambda: TemplateAnalysisService()
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()


def create_test_user(db_session: Session, discord_id: str, display_name: str, *, is_admin: bool = False) -> User:
    user = User(
        discord_id=discord_id,
        username=display_name.lower().replace(" ", "-"),
        display_name=display_name,
        avatar_url=None,
        slug=display_name.lower().replace(" ", "-"),
        is_admin=is_admin,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_avatar(db_session: Session, owner_id: str, title: str, *, is_primary: bool = False) -> Avatar:
    avatar = Avatar(
        owner_id=owner_id,
        title=title,
        description=None,
        image_url=f"http://testserver/uploads/{title}.png",
        storage_key=f"{owner_id}/{title}.png",
        content_hash=f"{owner_id}-{title}",
        mime_type="image/png",
        width=512,
        height=512,
        is_primary=is_primary,
    )
    db_session.add(avatar)
    db_session.commit()
    db_session.refresh(avatar)
    return avatar


def attach_session_cookie(client: TestClient, db_session: Session, user: User, *, cookie_name: str = "votee_session") -> str:
    token = create_session_token()
    login_session = LoginSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=session_expiry(),
    )
    db_session.add(login_session)
    db_session.commit()
    client.cookies.set(cookie_name, token)
    return token


def make_test_image_bytes(color: str = "navy") -> bytes:
    image = Image.new("RGB", (32, 32), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
