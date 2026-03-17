from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.dependencies import get_current_user
from app.models import Avatar
from app.models import AvatarStatus
from app.models import User
from app.schemas import AvatarSummary
from app.schemas import UserProfileResponse
from app.schemas import UserSummary

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


@router.get("/{slug}", response_model=UserProfileResponse)
def public_profile(
    slug: str,
    _: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserProfileResponse:
    user = session.scalar(select(User).where(User.slug == slug))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found.")
    avatars = list(
        session.scalars(
            select(Avatar).where(Avatar.owner_id == user.id, Avatar.status == AvatarStatus.PUBLIC.value).order_by(Avatar.created_at.desc())
        )
    )
    return UserProfileResponse(
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

