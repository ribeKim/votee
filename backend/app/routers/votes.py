from __future__ import annotations

from collections.abc import Sequence

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.models import Avatar
from app.models import AvatarStatus
from app.models import User
from app.models import Vote
from app.models import VotePairView
from app.schemas import VoteMatchAvatar
from app.schemas import VoteMatchResponse
from app.schemas import VoteSubmitRequest
from app.schemas import VoteSubmitResponse
from app.services.voting import update_elo

router = APIRouter(prefix="/api/votes", tags=["votes"])


def _pair_key(left_id: str, right_id: str) -> tuple[str, str]:
    return tuple(sorted((left_id, right_id)))


def _pick_pair(candidates: Sequence[Avatar], recent_pairs: set[tuple[str, str]]) -> tuple[Avatar, Avatar] | None:
    for left_index, left_avatar in enumerate(candidates):
        for right_avatar in candidates[left_index + 1 :]:
            if _pair_key(left_avatar.id, right_avatar.id) not in recent_pairs:
                return left_avatar, right_avatar
    if len(candidates) >= 2:
        return candidates[0], candidates[1]
    return None


@router.get("/match", response_model=VoteMatchResponse)
def get_match(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> VoteMatchResponse:
    recent_views = list(
        session.execute(
            select(VotePairView.left_avatar_id, VotePairView.right_avatar_id)
            .where(VotePairView.viewer_id == user.id)
            .order_by(desc(VotePairView.created_at))
            .limit(20)
        )
    )
    recent_pairs = {_pair_key(left_id, right_id) for left_id, right_id in recent_views}
    candidates = list(
        session.scalars(
            select(Avatar)
            .where(Avatar.status == AvatarStatus.PUBLIC.value, Avatar.owner_id != user.id)
            .order_by(func.random())
            .limit(8)
        )
    )
    selected = _pick_pair(candidates, recent_pairs)
    if selected is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not enough public avatars for voting.")
    left_avatar, right_avatar = selected
    pair_view = VotePairView(viewer_id=user.id, left_avatar_id=left_avatar.id, right_avatar_id=right_avatar.id)
    session.add(pair_view)
    session.commit()
    session.refresh(pair_view)
    return VoteMatchResponse(
        pair_view_id=pair_view.id,
        left=VoteMatchAvatar(
            id=left_avatar.id,
            title=left_avatar.title,
            image_url=left_avatar.image_url,
            owner_slug=session.scalar(select(User.slug).where(User.id == left_avatar.owner_id)) or "",
        ),
        right=VoteMatchAvatar(
            id=right_avatar.id,
            title=right_avatar.title,
            image_url=right_avatar.image_url,
            owner_slug=session.scalar(select(User.slug).where(User.id == right_avatar.owner_id)) or "",
        ),
    )


@router.post("", response_model=VoteSubmitResponse)
def submit_vote(
    payload: VoteSubmitRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> VoteSubmitResponse:
    pair_view = session.scalar(select(VotePairView).where(VotePairView.id == payload.pair_view_id, VotePairView.viewer_id == user.id))
    if pair_view is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voting pair not found.")
    expected_ids = {pair_view.left_avatar_id, pair_view.right_avatar_id}
    submitted_ids = {payload.winner_avatar_id, payload.loser_avatar_id}
    if expected_ids != submitted_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submitted avatars do not match the active pair.")
    if session.scalar(select(Vote).where(Vote.pair_view_id == pair_view.id)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vote already submitted.")
    winner = session.scalar(select(Avatar).where(Avatar.id == payload.winner_avatar_id))
    loser = session.scalar(select(Avatar).where(Avatar.id == payload.loser_avatar_id))
    if winner is None or loser is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    if winner.owner_id == user.id or loser.owner_id == user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot vote on your own avatar.")
    winner_rating, loser_rating = update_elo(winner.elo_rating, loser.elo_rating)
    winner.elo_rating = winner_rating
    winner.wins += 1
    loser.elo_rating = loser_rating
    loser.losses += 1
    session.add(Vote(voter_id=user.id, winner_avatar_id=winner.id, loser_avatar_id=loser.id, pair_view_id=pair_view.id))
    session.commit()
    return VoteSubmitResponse(winner_rating=winner.elo_rating, loser_rating=loser.elo_rating)

