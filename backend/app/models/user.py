"""User 모델 — 회원가입·로그인·내 정보 조회에서 사용한다."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import Gender, UserRole
from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            f"gender IN ('{Gender.MALE}', '{Gender.FEMALE}', '{Gender.NONE}')",
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
    gender: Mapped[str] = mapped_column(String(10), nullable=False, default=Gender.NONE)
    role: Mapped[str] = mapped_column(String(10), nullable=False, default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parties = relationship("Party", back_populates="creator", cascade="all, delete-orphan")
    memberships = relationship("PartyMember", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
