"""문의와 신고 대화 모델."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time import now_kst_naive


class SupportThread(Base):
    __tablename__ = "support_threads"
    __table_args__ = (
        CheckConstraint("kind IN ('inquiry', 'report')", name="ck_support_thread_kind"),
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved')",
            name="ck_support_thread_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    party_id: Mapped[int | None] = mapped_column(ForeignKey("parties.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=now_kst_naive, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=now_kst_naive,
        onupdate=now_kst_naive,
        nullable=False,
    )

    user = relationship("User", foreign_keys=[user_id])
    party = relationship("Party", foreign_keys=[party_id])
    messages = relationship(
        "SupportMessage",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="SupportMessage.created_at",
    )
    events = relationship(
        "SupportEvent",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="SupportEvent.created_at",
    )


class SupportMessage(Base):
    __tablename__ = "support_messages"
    __table_args__ = (
        CheckConstraint(
            "sender_role IN ('user', 'admin', 'system')",
            name="ck_support_message_sender_role",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("support_threads.id"), nullable=False, index=True)
    sender_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    sender_role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=now_kst_naive, nullable=False)

    thread = relationship("SupportThread", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_user_id])


class SupportEvent(Base):
    __tablename__ = "support_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('created', 'status')",
            name="ck_support_event_type",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("support_threads.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=now_kst_naive, nullable=False)

    thread = relationship("SupportThread", back_populates="events")
