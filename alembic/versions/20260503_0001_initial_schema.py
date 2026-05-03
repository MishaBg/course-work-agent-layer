"""initial schema

Revision ID: 20260503_0001
Revises: 
Create Date: 2026-05-03 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260503_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_table(
        "videos",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("total_fragments", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("uploaded_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_videos_uploaded_by_user_id"), "videos", ["uploaded_by_user_id"], unique=False)

    op.create_table(
        "video_fragments",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("video_id", sa.String(length=36), nullable=False),
        sa.Column("fragment_number", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("etag", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
        sa.UniqueConstraint("video_id", "fragment_number", name="uq_video_fragment_number"),
    )
    op.create_index(op.f("ix_video_fragments_video_id"), "video_fragments", ["video_id"], unique=False)

    op.create_table(
        "fragment_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("requested_video_id", sa.String(length=36), nullable=False),
        sa.Column("video_id", sa.String(length=36), nullable=True),
        sa.Column("fragment_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("storage_key", sa.String(length=512), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fragment_requests_created_at"), "fragment_requests", ["created_at"], unique=False)
    op.create_index(op.f("ix_fragment_requests_requested_video_id"), "fragment_requests", ["requested_video_id"], unique=False)
    op.create_index(op.f("ix_fragment_requests_user_id"), "fragment_requests", ["user_id"], unique=False)
    op.create_index(op.f("ix_fragment_requests_video_id"), "fragment_requests", ["video_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fragment_requests_video_id"), table_name="fragment_requests")
    op.drop_index(op.f("ix_fragment_requests_user_id"), table_name="fragment_requests")
    op.drop_index(op.f("ix_fragment_requests_requested_video_id"), table_name="fragment_requests")
    op.drop_index(op.f("ix_fragment_requests_created_at"), table_name="fragment_requests")
    op.drop_table("fragment_requests")

    op.drop_index(op.f("ix_video_fragments_video_id"), table_name="video_fragments")
    op.drop_table("video_fragments")

    op.drop_index(op.f("ix_videos_uploaded_by_user_id"), table_name="videos")
    op.drop_table("videos")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
