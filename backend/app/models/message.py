"""Message 모델 — 파티별 채팅 메시지를 저장한다."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time import now_kst_naive


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=now_kst_naive, nullable=False
    )
    # 관리자 메시지 숨김 — ADMIN-026.
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hidden_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    hidden_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    # 관리자 공지 메시지 — ADMIN-027.
    is_admin_notice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    party = relationship("Party", back_populates="messages")
    user = relationship("User", back_populates="messages", foreign_keys=[user_id])
