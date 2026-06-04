"""AdminAction 모델 — 관리자 조작 기록 (admin_actions).

명세서 v0.4 ADMIN-012 / data-model 'admin_actions 테이블':
  · role 변경, 사용자 활성 상태 변경, 관리자 파티 상태 변경을 반드시 기록한다.
  · 실제 신고/결제 이력이 아니라 MVP 관리자 조작 이력이다.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.time import now_kst_naive


class AdminAction(Base):
    __tablename__ = "admin_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_admin_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    # user_role_update / user_status_update / party_status_update
    action_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user / party
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    before_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    after_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=now_kst_naive, nullable=False
    )

    actor = relationship("User")
