from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import attach_session_cookie
from tests.conftest import create_test_avatar
from tests.conftest import create_test_user
from tests.conftest import make_test_image_bytes


def test_avatar_upload_rejects_duplicate_payloads(client: TestClient, db_session: Session) -> None:
    user = create_test_user(db_session, "uploader-1", "Uploader One")
    attach_session_cookie(client, db_session, user)
    file_payload = make_test_image_bytes()
    first_response = client.post(
        "/api/avatars",
        files={"file": ("avatar.png", file_payload, "image/png")},
        data={"title": "My Avatar", "description": "primary cut"},
    )
    second_response = client.post(
        "/api/avatars",
        files={"file": ("avatar.png", file_payload, "image/png")},
        data={"title": "My Avatar Again", "description": "duplicate"},
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_vote_match_excludes_owned_avatar_and_updates_elo(client: TestClient, db_session: Session) -> None:
    voter = create_test_user(db_session, "voter-1", "Voter One")
    owner_one = create_test_user(db_session, "owner-1", "Owner One")
    owner_two = create_test_user(db_session, "owner-2", "Owner Two")
    own_avatar = create_test_avatar(db_session, voter.id, "own-avatar")
    first_public = create_test_avatar(db_session, owner_one.id, "first-public")
    second_public = create_test_avatar(db_session, owner_two.id, "second-public")
    attach_session_cookie(client, db_session, voter)
    match_response = client.get("/api/votes/match")
    assert match_response.status_code == 200
    payload = match_response.json()
    returned_ids = {payload["left"]["id"], payload["right"]["id"]}
    assert own_avatar.id not in returned_ids
    assert returned_ids == {first_public.id, second_public.id}
    winner_id = payload["left"]["id"]
    loser_id = payload["right"]["id"]
    vote_response = client.post(
        "/api/votes",
        json={
            "pair_view_id": payload["pair_view_id"],
            "winner_avatar_id": winner_id,
            "loser_avatar_id": loser_id,
        },
    )
    assert vote_response.status_code == 200
    rating_payload = vote_response.json()
    assert rating_payload["winner_rating"] != rating_payload["loser_rating"]
