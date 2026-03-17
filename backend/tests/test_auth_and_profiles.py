from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from tests.conftest import attach_session_cookie
from tests.conftest import create_test_avatar
from tests.conftest import create_test_user


def test_discord_callback_creates_session_and_current_user(client: TestClient, db_session: Session) -> None:
    login_response = client.get("/api/auth/discord/login", follow_redirects=False)
    assert login_response.status_code == 302
    callback_response = client.get("/api/auth/discord/callback?code=test-code-1001&state=" + client.cookies["votee_oauth_state"], follow_redirects=False)
    assert callback_response.status_code == 302
    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["user"]["display_name"] == "User 1001"


def test_public_profile_returns_only_public_avatars(client: TestClient, db_session: Session) -> None:
    viewer = create_test_user(db_session, "viewer-1", "Viewer One")
    profile_user = create_test_user(db_session, "artist-1", "Artist One")
    attach_session_cookie(client, db_session, viewer)
    create_test_avatar(db_session, profile_user.id, "profile-card", is_primary=True)
    response = client.get(f"/api/profiles/{profile_user.slug}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["slug"] == profile_user.slug
    assert len(payload["avatars"]) == 1
