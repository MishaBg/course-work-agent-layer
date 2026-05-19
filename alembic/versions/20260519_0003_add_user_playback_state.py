"""add user playback state

Revision ID: 20260519_0003
Revises: 20260503_0002
Create Date: 2026-05-19 20:55:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260519_0003"
down_revision: Union[str, None] = "20260503_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_video_id", sa.String(length=36), nullable=True))
    op.add_column("users", sa.Column("last_position_seconds", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("users", "last_position_seconds")
    op.drop_column("users", "last_video_id")
