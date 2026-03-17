from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.dependencies import get_admin_user
from app.models import AdminAction
from app.models import Avatar
from app.models import AvatarStatus
from app.models import Report
from app.models import ReportStatus
from app.models import User
from app.schemas import AdminActionRequest
from app.schemas import AdminReportItem

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _record_admin_action(session: Session, admin_user: User, target_type: str, target_id: str, action: str, note: str | None) -> None:
    session.add(
        AdminAction(
            admin_user_id=admin_user.id,
            target_type=target_type,
            target_id=target_id,
            action=action,
            note=note,
        )
    )


@router.get("/reports", response_model=list[AdminReportItem])
def list_reports(
    _: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
) -> list[AdminReportItem]:
    reports = list(session.scalars(select(Report).order_by(Report.created_at.desc())))
    items: list[AdminReportItem] = []
    for report in reports:
        avatar = session.scalar(select(Avatar).where(Avatar.id == report.avatar_id))
        reporter = session.scalar(select(User).where(User.id == report.reporter_id))
        if avatar is None or reporter is None:
            continue
        items.append(
            AdminReportItem(
                id=report.id,
                avatar_id=report.avatar_id,
                avatar_title=avatar.title,
                reporter_slug=reporter.slug,
                reason=report.reason,
                status=report.status,
                created_at=report.created_at,
            )
        )
    return items


@router.post("/avatars/{avatar_id}/hide", status_code=status.HTTP_204_NO_CONTENT)
def hide_avatar(
    avatar_id: str,
    payload: AdminActionRequest,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
) -> None:
    avatar = session.scalar(select(Avatar).where(Avatar.id == avatar_id))
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    avatar.status = AvatarStatus.HIDDEN.value
    _record_admin_action(session, admin_user, "avatar", avatar.id, "hide", payload.note)
    for report in session.scalars(select(Report).where(Report.avatar_id == avatar.id, Report.status == ReportStatus.OPEN.value)):
        report.status = ReportStatus.RESOLVED.value
    session.commit()


@router.post("/avatars/{avatar_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(
    avatar_id: str,
    payload: AdminActionRequest,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
) -> None:
    avatar = session.scalar(select(Avatar).where(Avatar.id == avatar_id))
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    avatar.status = AvatarStatus.DELETED.value
    _record_admin_action(session, admin_user, "avatar", avatar.id, "delete", payload.note)
    for report in session.scalars(select(Report).where(Report.avatar_id == avatar.id, Report.status == ReportStatus.OPEN.value)):
        report.status = ReportStatus.RESOLVED.value
    session.commit()


@router.post("/users/{user_id}/suspend", status_code=status.HTTP_204_NO_CONTENT)
def suspend_user(
    user_id: str,
    payload: AdminActionRequest,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
) -> None:
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_suspended = True
    _record_admin_action(session, admin_user, "user", user.id, "suspend", payload.note)
    session.commit()

