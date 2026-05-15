"""파티 도메인 서비스 — 상태 계산, 응답 직렬화 등 라우터에서 재사용하는 로직."""

from __future__ import annotations

from datetime import datetime

from app.constants import PartyStatus
from app.models import Party
from app.schemas.party import PartyDetail, PartyMemberOut, PartySummary
from app.services.fare import per_person_fare
from app.utils.time import now_kst_naive, to_kst_naive


def effective_status(party: Party, now: datetime | None = None) -> str:
    """저장된 status를 그대로 쓰되, recruiting + 출발시각 지남이면 expired로 취급한다.

    기능명세서 F-PARTY-011: '조회 시 expired로 취급' 옵션을 채택한다.
    """
    current_time = now or now_kst_naive()
    if party.status == PartyStatus.RECRUITING:
        if to_kst_naive(party.departure_time) < current_time:
            return PartyStatus.EXPIRED
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
        creator=party.creator,
        members=[PartyMemberOut(user=m.user, joined_at=m.joined_at) for m in party.members],
    )


def sync_status_after_join(party: Party) -> None:
    """참여 후 인원이 max에 도달하면 status=matched로 갱신한다 — F-PARTY-004."""
    if len(party.members) >= party.max_members and party.status == PartyStatus.RECRUITING:
        party.status = PartyStatus.MATCHED
