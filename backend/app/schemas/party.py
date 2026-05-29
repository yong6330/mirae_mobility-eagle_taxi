"""파티 관련 Pydantic 스키마 — 기능명세서 F-PARTY-001 ~ 004."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import GenderRule, GenderRuleType, GenderType, PartyStatusType


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
    """파티 참여자 응답 항목 — 명세 v0.4 PARTY-005/006 members: {id, name, gender}."""

    id: int
    name: str
    gender: GenderType


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
    creator_name: str
    members: list[PartyMemberOut]


class PartyJoinResponse(BaseModel):
    """파티 참여 성공 응답 — 명세 v0.4 PARTY-006.

    result_code/can_join/reason 래퍼 + 갱신된 인원·요금·상태·참여자 목록.
    실패는 기존과 동일하게 HTTPException + detail로 처리한다 (에러 코드 세분화는 회의 대기).
    """

    result_code: int
    can_join: bool
    reason: str
    id: int
    current_members: int
    max_members: int
    estimated_fare: int
    per_person_fare: int
    status: PartyStatusType
    members: list[PartyMemberOut]


class PartyListResponse(BaseModel):
    """파티 목록 응답 — 기능명세서 F-PARTY-002 출력값 (목록 + 페이지 메타)."""

    parties: list[PartySummary]
    total: int
    page: int
    limit: int


class FareEstimateOut(BaseModel):
    """예상 요금 미리보기 응답 — 기능명세서 F-PARTY-005 / FARE-001.

    파티 생성 전 좌표만 가지고 예상치를 미리 보여주는 용도.
    1인 요금(per_person_fare)은 파티 인원이 아직 정해지지 않았으므로 포함하지 않는다.
    """

    estimated_fare: int
    toll_fare: int
    distance_meters: int
    duration_seconds: int
    fare_source: str


class MyPartiesResponse(BaseModel):
    """내 파티 목록 응답 — 기능명세서 v0.4 F-PARTY-009.

    생성자는 created_parties에만 표시하고 joined_parties에 중복 노출하지 않는다.
    """

    created_parties: list[PartySummary]
    joined_parties: list[PartySummary]


class PartyCancelRequest(BaseModel):
    """PATCH /api/parties/{id}/cancel 요청 Body — 기능명세서 v0.4 F-PARTY-011."""

    cancel_reason: str | None = Field(default=None, max_length=500)


class RecommendedParty(PartySummary):
    """추천 응답 항목 — 명세서 v0.4 F-PARTY-008.

    PartySummary에 match_score(0~100)와 만남 정보를 추가한다.
    """

    match_score: int
    meeting_point: str | None = None
    meeting_note: str | None = None


class RecommendResponse(BaseModel):
    """유사 파티 추천 응답 — 명세서 v0.4 F-PARTY-008."""

    parties: list[RecommendedParty]
