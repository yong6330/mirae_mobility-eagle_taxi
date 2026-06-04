"""User 모델 — 회원가입·로그인·내 정보 조회에서 사용한다."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import Gender, UserRole
from app.database import Base
from app.utils.time import now_kst_naive


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        # 명세서 v0.4: gender는 male/female만. none은 시스템 내부값 (DB 저장값으로 사용 X).
        CheckConstraint(
            f"gender IN ('{Gender.MALE}', '{Gender.FEMALE}')",
            name="ck_user_gender",
        ),
        CheckConstraint(
            f"role IN ('{UserRole.USER}', '{UserRole.ADMIN}')",
            name="ck_user_role",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)  # male / female
    role: Mapped[str] = mapped_column(String(10), nullable=False, default=UserRole.USER)
    # 명세서 v0.4 F-ACCOUNT-001 / F-ADMIN-007: 관리자가 비활성화할 수 있는 플래그.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=now_kst_naive, nullable=False
    )

    parties = relationship("Party", back_populates="creator", cascade="all, delete-orphan")
    memberships = relationship("PartyMember", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

    @property
    def master_admin(self) -> bool:
        """마스터 관리자 여부 — MASTER_ADMIN_EMAILS 기준 (명세 §3주차 보완).

        응답 스키마(UserOut 등)가 from_attributes로 읽어간다.
        """
        from app.config import settings

        return self.email.lower() in settings.master_admin_email_set
