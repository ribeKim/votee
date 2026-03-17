from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class UserSummary(BaseModel):
    id: str
    display_name: str
    username: str
    slug: str
    avatar_url: str | None
    bio: str | None
    is_admin: bool


class AvatarSummary(BaseModel):
    id: str
    title: str
    description: str | None
    image_url: str
    status: str
    is_primary: bool
    elo_rating: int
    wins: int
    losses: int
    width: int
    height: int
    created_at: datetime


class UserProfileResponse(BaseModel):
    user: UserSummary
    avatars: list[AvatarSummary]


class AuthenticatedUserResponse(BaseModel):
    user: UserSummary
    avatars: list[AvatarSummary]


class AvatarUploadResponse(BaseModel):
    avatar: AvatarSummary


class PrimaryAvatarRequest(BaseModel):
    avatar_id: str


class VoteMatchAvatar(BaseModel):
    id: str
    title: str
    image_url: str
    owner_slug: str


class VoteMatchResponse(BaseModel):
    pair_view_id: str
    left: VoteMatchAvatar
    right: VoteMatchAvatar


class VoteSubmitRequest(BaseModel):
    pair_view_id: str
    winner_avatar_id: str
    loser_avatar_id: str


class VoteSubmitResponse(BaseModel):
    winner_rating: int
    loser_rating: int


class ReportCreateRequest(BaseModel):
    avatar_id: str
    reason: str = Field(min_length=5, max_length=500)


class ReportResponse(BaseModel):
    id: str
    avatar_id: str
    reason: str
    status: str
    created_at: datetime


class AdminActionRequest(BaseModel):
    note: str | None = Field(default=None, max_length=500)


class AdminReportItem(BaseModel):
    id: str
    avatar_id: str
    avatar_title: str
    reporter_slug: str
    reason: str
    status: str
    created_at: datetime


class AnalysisTriggerResponse(BaseModel):
    request_id: str
    status: str


class AnalysisResultResponse(BaseModel):
    request_id: str
    avatar_id: str
    status: str
    summary: str | None
    strengths: str | None
    style_notes: str | None
    improvement_tips: str | None
    error_message: str | None

