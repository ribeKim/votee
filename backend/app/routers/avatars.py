from __future__ import annotations

from io import BytesIO
import hashlib

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from PIL import Image
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import get_session
from app.dependencies import get_app_settings
from app.dependencies import get_current_user
from app.dependencies import get_storage_service
from app.models import Avatar
from app.models import Report
from app.models import User
from app.schemas import AvatarSummary
from app.schemas import AvatarUploadResponse
from app.schemas import PrimaryAvatarRequest
from app.schemas import ReportCreateRequest
from app.schemas import ReportResponse
from app.services.storage import StorageService

router = APIRouter(prefix="/api/avatars", tags=["avatars"])


def _serialize_avatar(avatar: Avatar) -> AvatarSummary:
    return AvatarSummary(
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


@router.post("", response_model=AvatarUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str | None = Form(default=None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    settings: Settings = Depends(get_app_settings),
    storage: StorageService = Depends(get_storage_service),
) -> AvatarUploadResponse:
    if file.content_type not in settings.allowed_image_type_set:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type.")
    payload = await file.read()
    if len(payload) > settings.max_upload_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is too large.")
    digest = hashlib.sha256(payload).hexdigest()
    if session.scalar(select(Avatar).where(Avatar.content_hash == digest)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate avatar upload.")
    try:
        image = Image.open(BytesIO(payload))
        width, height = image.size
    except OSError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image payload.") from error
    stored = await storage.upload_avatar(user.id, file.content_type or "application/octet-stream", payload)
    should_be_primary = session.scalar(select(Avatar).where(Avatar.owner_id == user.id, Avatar.is_primary.is_(True))) is None
    avatar = Avatar(
        owner_id=user.id,
        title=title.strip(),
        description=description.strip() if description else None,
        image_url=stored.public_url,
        storage_key=stored.object_key,
        content_hash=digest,
        mime_type=file.content_type or "application/octet-stream",
        width=width,
        height=height,
        is_primary=should_be_primary,
    )
    session.add(avatar)
    session.commit()
    session.refresh(avatar)
    return AvatarUploadResponse(avatar=_serialize_avatar(avatar))


@router.post("/primary", response_model=AvatarUploadResponse)
def set_primary_avatar(
    payload: PrimaryAvatarRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AvatarUploadResponse:
    avatar = session.scalar(select(Avatar).where(Avatar.id == payload.avatar_id, Avatar.owner_id == user.id))
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    session.execute(update(Avatar).where(Avatar.owner_id == user.id).values(is_primary=False))
    avatar.is_primary = True
    session.commit()
    session.refresh(avatar)
    return AvatarUploadResponse(avatar=_serialize_avatar(avatar))


@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    payload: ReportCreateRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ReportResponse:
    avatar = session.scalar(select(Avatar).where(Avatar.id == payload.avatar_id))
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    report = Report(reporter_id=user.id, avatar_id=avatar.id, reason=payload.reason)
    session.add(report)
    session.commit()
    session.refresh(report)
    return ReportResponse(
        id=report.id,
        avatar_id=report.avatar_id,
        reason=report.reason,
        status=report.status,
        created_at=report.created_at,
    )

