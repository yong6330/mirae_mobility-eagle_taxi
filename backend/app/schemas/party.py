"""파티 관련 Pydantic 스키마 — 기능명세서 F-PARTY-001 ~ 004."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import GenderRule, GenderRuleType, PartyStatusType
from app.schemas.auth import UserOut


class PartyCreateRequest(BaseModel):
    """POST /api/parties 요청 Body — 기능명세서 F-PARTY-001 입력값."""

    start_place: str = Field(min_length=1, max_length=200)
    start_lat: float
    start_lng: float
    end_place: str = Field(min_length=1, max_length=200)
    end_lat: float
    end_lng: float
    departure_time: datetime  # KST 기준 ISO 8601
    meeting_point: str | None = Field(default=None, max_length=200)
    meeting_note: str | None = None
    max_members: int = Field(ge=2, le=4)  # F-PARTY-001: 2~4명
    gender_rule: GenderRuleType = GenderRule.ANY


class PartyMemberOut(BaseModel):
    """파티 참여자 응답 — 상세 조회의 참여자 목록에 사용."""

    model_config = ConfigDict(from_attributes=True)

    user: UserOut
    joined_at: datetime


class PartySummary(BaseModel):
    """파티 목록·생성 응답 — 요약 정보. 1인 요금은 계산값."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    creator_id: int
    start_place: str
    end_place: str
    departure_time: datetime
    max_members: int
    current_members: int
    estimated_fare: int
    per_person_fare: int
    status: PartyStatusType
    gender_rule: GenderRuleType
    created_at: datetime


class PartyDetail(PartySummary):
    """파티 상세 응답 — 기능명세서 F-PARTY-003 출력값 전부."""

    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    meeting_point: str | None = None
    meeting_note: str | None = None
    toll_fare: int
    distance_meters: int
    duration_seconds: int
    fare_source: str
    party_gender: str | None = None
    canceled_at: datetime | None = None
    cancel_reason: str | None = None
    creator: UserOut
    members: list[PartyMemberOut]


class PartyListResponse(BaseModel):
    """파티 목록 응답 — 기능명세서 F-PARTY-002 출력값 (목록 + 페이지 메타)."""

    parties: list[PartySummary]
    total: int
    page: int
    limit: int
