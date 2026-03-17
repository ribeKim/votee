from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.dependencies import get_analysis_service
from app.dependencies import get_current_user
from app.models import AnalysisRequest
from app.models import AnalysisResult
from app.models import AnalysisStatus
from app.models import Avatar
from app.models import User
from app.schemas import AnalysisResultResponse
from app.schemas import AnalysisTriggerResponse
from app.security import now_utc
from app.services.analysis import AnalysisService

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/avatars/{avatar_id}/analysis", response_model=AnalysisTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_analysis(
    avatar_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    analysis_service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisTriggerResponse:
    avatar = session.scalar(select(Avatar).where(Avatar.id == avatar_id, Avatar.owner_id == user.id))
    if avatar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found.")
    request = AnalysisRequest(avatar_id=avatar.id, owner_id=user.id, status=AnalysisStatus.PENDING.value)
    session.add(request)
    session.commit()
    session.refresh(request)
    try:
        generated = await analysis_service.analyze_avatar(
            title=avatar.title,
            description=avatar.description,
            image_url=avatar.image_url,
            width=avatar.width,
            height=avatar.height,
        )
        session.add(
            AnalysisResult(
                request_id=request.id,
                summary=generated.summary,
                strengths=generated.strengths,
                style_notes=generated.style_notes,
                improvement_tips=generated.improvement_tips,
            )
        )
        request.status = AnalysisStatus.COMPLETED.value
        request.completed_at = now_utc()
        session.commit()
    except Exception as error:
        request.status = AnalysisStatus.FAILED.value
        request.error_message = str(error)
        request.completed_at = now_utc()
        session.commit()
    return AnalysisTriggerResponse(request_id=request.id, status=request.status)


@router.get("/analysis/{request_id}", response_model=AnalysisResultResponse)
def get_analysis_result(
    request_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> AnalysisResultResponse:
    request = session.scalar(select(AnalysisRequest).where(AnalysisRequest.id == request_id, AnalysisRequest.owner_id == user.id))
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis request not found.")
    result = session.scalar(select(AnalysisResult).where(AnalysisResult.request_id == request.id))
    return AnalysisResultResponse(
        request_id=request.id,
        avatar_id=request.avatar_id,
        status=request.status,
        summary=result.summary if result else None,
        strengths=result.strengths if result else None,
        style_notes=result.style_notes if result else None,
        improvement_tips=result.improvement_tips if result else None,
        error_message=request.error_message,
    )

