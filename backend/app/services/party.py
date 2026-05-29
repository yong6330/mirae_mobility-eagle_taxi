"""파티 도메인 서비스 — 명세서 v0.4 F-PARTY-006/012."""

from __future__ import annotations

from datetime import datetime

from app.constants import PartyStatus
from app.models import Party
from app.schemas.party import PartyDetail, PartyJoinResponse, PartyMemberOut, PartySummary
from app.services.fare import per_person_fare
from app.utils.time import now_kst_naive, to_kst_naive


def _members_out(party: Party) -> list[PartyMemberOut]:
    """참여자 목록을 명세 v0.4 members: {id, name, gender} 형태로 변환."""
    return [
        PartyMemberOut(id=m.user.id, name=m.user.name, gender=m.user.gender)
        for m in party.members
    ]


def effective_status(party: Party, now: datetime | None = None) -> str:
    """저장된 status를 기준으로, 시간 경과를 반영해 실효 상태를 계산한다.

    명세서 v0.4 F-PARTY-006 / F-PARTY-012:
      - status=recruiting + departure_time 지남 → expired
      - status=matched + departure_time 지남 → completed
      - canceled, expired, completed는 그대로 유지
    저장된 DB 값은 안 바꾸고, 응답·검증 시점에만 계산값을 사용한다.
    """
    current_time = now or now_kst_naive()
    departure = to_kst_naive(party.departure_time)
    if party.status == PartyStatus.RECRUITING and departure < current_time:
        return PartyStatus.EXPIRED
    if party.status == PartyStatus.MATCHED and departure < current_time:
        return PartyStatus.COMPLETED
    return party.status


def to_summary(party: Party) -> PartySummary:
    """Party 모델을 목록용 응답으로 변환한다."""
    current = len(party.members)
    return PartySummary(
        id=party.id,
        creator_id=party.creator_id,
        start_place=party.start_place,
        end_place=party.end_place,
        departure_time=party.departure_time,
        max_members=party.max_members,
        current_members=current,
        estimated_fare=party.estimated_fare,
        per_person_fare=per_person_fare(party.estimated_fare, current),
        status=effective_status(party),
        gender_rule=party.gender_rule,
        created_at=party.created_at,
    )


def to_detail(party: Party) -> PartyDetail:
    """Party 모델을 상세 조회 응답으로 변환한다."""
    current = len(party.members)
    return PartyDetail(
        id=party.id,
        creator_id=party.creator_id,
        start_place=party.start_place,
        start_lat=party.start_lat,
        start_lng=party.start_lng,
        end_place=party.end_place,
        end_lat=party.end_lat,
        end_lng=party.end_lng,
        departure_time=party.departure_time,
        meeting_point=party.meeting_point,
        meeting_note=party.meeting_note,
        max_members=party.max_members,
        current_members=current,
        gender_rule=party.gender_rule,
        party_gender=party.party_gender,
        estimated_fare=party.estimated_fare,
        toll_fare=party.toll_fare,
        distance_meters=party.distance_meters,
        duration_seconds=party.duration_seconds,
        fare_source=party.fare_source,
        per_person_fare=per_person_fare(party.estimated_fare, current),
        status=effective_status(party),
        created_at=party.created_at,
        canceled_at=party.canceled_at,
        cancel_reason=party.cancel_reason,
        creator_name=party.creator.name,
        members=_members_out(party),
    )


def to_join_response(party: Party) -> PartyJoinResponse:
    """참여 성공 응답 — 명세 v0.4 PARTY-006 (result_code/can_join/reason 래퍼)."""
    current = len(party.members)
    return PartyJoinResponse(
        result_code=200,
        can_join=True,
        reason="파티에 참여하였습니다.",
        id=party.id,
        current_members=current,
        max_members=party.max_members,
        estimated_fare=party.estimated_fare,
        per_person_fare=per_person_fare(party.estimated_fare, current),
        status=effective_status(party),
        members=_members_out(party),
    )


def sync_status_after_join(party: Party) -> None:
    """참여 후 인원이 max에 도달하면 status=matched로 갱신 — F-PARTY-004."""
    if len(party.members) >= party.max_members and party.status == PartyStatus.RECRUITING:
        party.status = PartyStatus.MATCHED
