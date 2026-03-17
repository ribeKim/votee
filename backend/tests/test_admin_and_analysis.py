from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import AnalysisRequest
from app.models import Avatar
from app.models import Report
from tests.conftest import attach_session_cookie
from tests.conftest import create_test_avatar
from tests.conftest import create_test_user


def test_admin_hide_marks_avatar_hidden_and_resolves_report(client: TestClient, db_session: Session) -> None:
    admin = create_test_user(db_session, "discord-admin", "Admin User", is_admin=True)
    reporter = create_test_user(db_session, "reporter-1", "Reporter One")
    owner = create_test_user(db_session, "owner-1", "Owner One")
    avatar = create_test_avatar(db_session, owner.id, "reportable-avatar")
    report = Report(reporter_id=reporter.id, avatar_id=avatar.id, reason="부적절한 설정")
    db_session.add(report)
    db_session.commit()
    attach_session_cookie(client, db_session, admin)
    response = client.post(f"/api/admin/avatars/{avatar.id}/hide", json={"note": "hidden by test"})
    db_session.refresh(avatar)
    db_session.refresh(report)
    assert response.status_code == 204
    assert avatar.status == "hidden"
    assert report.status == "resolved"


def test_analysis_is_owner_only(client: TestClient, db_session: Session) -> None:
    owner = create_test_user(db_session, "owner-analysis", "Owner Analysis")
    other_user = create_test_user(db_session, "other-analysis", "Other Analysis")
    avatar = create_test_avatar(db_session, owner.id, "analysis-avatar")
    attach_session_cookie(client, db_session, owner)
    trigger_response = client.post(f"/api/avatars/{avatar.id}/analysis")
    assert trigger_response.status_code == 202
    request_id = trigger_response.json()["request_id"]
    success_response = client.get(f"/api/analysis/{request_id}")
    assert success_response.status_code == 200
    client.cookies.clear()
    attach_session_cookie(client, db_session, other_user)
    forbidden_response = client.get(f"/api/analysis/{request_id}")
    assert forbidden_response.status_code == 404
