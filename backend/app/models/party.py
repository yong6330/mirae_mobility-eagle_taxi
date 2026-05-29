"""Party 모델 — 파티 생성·목록·상세·참여·취소 등 모든 파티 API의 핵심 테이블."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import FareSource, Gender, GenderRule, PartyStatus
from app.database import Base


def _in_list_constraint(column_name: str, allowed: tuple[str, ...], name: str) -> CheckConstraint:
    """`column IN ('a','b',...)` 형태 체크 제약을 만든다."""
    quoted = ", ".join(f"'{value}'" for value in allowed)
    return CheckConstraint(f"{column_name} IN ({quoted})", name=name)


class Party(Base):
    __tablename__ = "parties"
    __table_args__ = (
        _in_list_constraint("status", PartyStatus.ALL, "ck_party_status"),
        _in_list_constraint("gender_rule", GenderRule.ALL, "ck_party_gender_rule"),
        _in_list_constraint("fare_source", FareSource.ALL, "ck_party_fare_source"),
        # party_gender는 nullable이므로 NULL OR {male,female} 형태로 허용한다.
        CheckConstraint(
            f"party_gender IS NULL OR party_gender IN ('{Gender.MALE}', '{Gender.FEMALE}')",
            name="ck_party_party_gender",
        ),
        CheckConstraint("max_members BETWEEN 2 AND 4", name="ck_party_max_members"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # ─ 출발지 / 도착지 (Kakao Maps 좌표) ─────────────────────────────
    start_place: Mapped[str] = mapped_column(String(200), nullable=False)
    start_lat: Mapped[float] = mapped_column(Float, nullable=False)
    start_lng: Mapped[float] = mapped_column(Float, nullable=False)
    end_place: Mapped[str] = mapped_column(String(200), nullable=False)
    end_lat: Mapped[float] = mapped_column(Float, nullable=False)
    end_lng: Mapped[float] = mapped_column(Float, nullable=False)

    # ─ 일정 / 만남 ─────────────────────────────────────────────────
    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    meeting_point: Mapped[str | None] = mapped_column(String(200), nullable=True)
    meeting_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─ 정원 / 매칭 옵션 ────────────────────────────────────────────
    max_members: Mapped[int] = mapped_column(Integer, nullable=False)
    gender_rule: Mapped[str] = mapped_column(String(20), nullable=False, default=GenderRule.ANY)
    # F-PARTY-013: gender_rule=same_gender일 때 생성자 성별을 여기 저장하고,
    # 참여 요청 시 이 값과 비교한다. any면 NULL.
    party_gender: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # ─ Kakao Mobility 산정 결과 (Key 없으면 모두 0) ─────────────────
    estimated_fare: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    toll_fare: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    distance_meters: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # F-PARTY-005 출력값: 요금 출처 — "kakao_mobility" 또는 "fallback" (Key 없을 때).
    fare_source: Mapped[str] = mapped_column(
        String(20), nullable=False, default=FareSource.FALLBACK
    )

    # ─ 상태 / 타임스탬프 ───────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PartyStatus.RECRUITING, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # F-PARTY-010: 파티 취소 시 사유 저장.
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    creator = relationship("User", back_populates="parties")
    members = relationship("PartyMember", back_populates="party", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="party", cascade="all, delete-orphan")
