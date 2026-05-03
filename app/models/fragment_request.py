from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FragmentRequestStatus(StrEnum):
    ACCEPTED = "accepted"
    FOUND = "found"
    NOT_FOUND = "not_found"
    FAILED = "failed"


class FragmentRequest(Base):
    __tablename__ = "fragment_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    requested_video_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    video_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("videos.id", ondelete="RESTRICT"), index=True, nullable=True)
    fragment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=FragmentRequestStatus.ACCEPTED.value, nullable=False)
    storage_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
