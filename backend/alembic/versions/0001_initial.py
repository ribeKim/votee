"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("discord_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("slug", sa.String(length=160), nullable=False, unique=True),
        sa.Column("bio", sa.String(length=280), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_suspended", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "avatars",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=280), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(length=64), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("elo_rating", sa.Integer(), nullable=False, server_default="1200"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("losses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "vote_pair_views",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("viewer_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("left_avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("right_avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "votes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("voter_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("winner_avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("loser_avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("pair_view_id", sa.String(length=36), sa.ForeignKey("vote_pair_views.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("reporter_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "admin_actions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("admin_user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target_id", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "analysis_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("avatar_id", sa.String(length=36), sa.ForeignKey("avatars.id"), nullable=False),
        sa.Column("owner_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "analysis_results",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("request_id", sa.String(length=36), sa.ForeignKey("analysis_requests.id"), nullable=False, unique=True),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("strengths", sa.String(length=1000), nullable=False),
        sa.Column("style_notes", sa.String(length=1000), nullable=False),
        sa.Column("improvement_tips", sa.String(length=1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("analysis_results")
    op.drop_table("analysis_requests")
    op.drop_table("admin_actions")
    op.drop_table("reports")
    op.drop_table("votes")
    op.drop_table("vote_pair_views")
    op.drop_table("avatars")
    op.drop_table("sessions")
    op.drop_table("users")
