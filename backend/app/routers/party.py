"""파티 라우터 — 명세서 v0.4 F-PARTY-001 ~ 011."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.constants import Gender, GenderRule, PartyStatus, PartyStatusType
from app.database import get_db
from app.deps import get_current_user
from app.models import Party, PartyMember, User
from app.schemas.party import (
    PartyCancelRequest,
    PartyCreateRequest,
    PartyDetail,
    PartyListResponse,
    RecommendedParty,
    RecommendResponse,
)
from app.services.fare import estimate_fare
from app.services.party import effective_status, sync_status_after_join, to_detail, to_summary
from app.utils.time import now_kst_naive, to_kst_naive

router = APIRouter(prefix="/api/parties", tags=["parties"])

# 같은 시간대 중복 참여 검증의 허용 간격 — 명세서 v0.4 F-PARTY-004.
# 두 파티의 출발 시간이 이 간격 미만이면 "같은 시간대"로 보고 중복 참여를 차단한다.
TIME_CONFLICT_WINDOW = timedelta(minutes=60)


def _load_party_with_relations(db: Session, party_id: int) -> Party | None:
    """파티를 members·creator·users 관계까지 한 번에 로드 (N+1 방지)."""
    stmt = (
        select(Party)
        .where(Party.id == party_id)
        .options(
            selectinload(Party.creator),
            selectinload(Party.members).selectinload(PartyMember.user),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def _has_time_conflict(db: Session, user_id: int, departure_time, exclude_party_id: int | None = None) -> bool:
    """user_id가 지정 시각 근처에 이미 활성 파티에 참여 중인지 확인 — F-PARTY-004."""
    target = to_kst_naive(departure_time)
    window_start = target - TIME_CONFLICT_WINDOW
    window_end = target + TIME_CONFLICT_WINDOW

    stmt = (
        select(Party)
        .join(PartyMember, PartyMember.party_id == Party.id)
        .where(PartyMember.user_id == user_id)
        .where(Party.status.in_([PartyStatus.RECRUITING, PartyStatus.MATCHED]))
        .where(Party.departure_time >= window_start)
        .where(Party.departure_time <= window_end)
    )
    if exclude_party_id is not None:
        stmt = stmt.where(Party.id != exclude_party_id)
    return db.execute(stmt).scalar_one_or_none() is not None


@router.post("", response_model=PartyDetail, status_code=status.HTTP_201_CREATED)
def create_party(
    payload: PartyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 생성 — 명세서 v0.4 F-PARTY-001."""
    departure = to_kst_naive(payload.departure_time)
    if departure <= now_kst_naive():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="출발 시간은 현재 시각 이후여야 합니다.",
        )

    party_gender: str | None = None
    if payload.gender_rule == GenderRule.SAME_GENDER:
        # 명세 v0.4 F-PARTY-014: gender=none인 사용자(이론상 회원가입 차단됐지만 안전망)는
        # same_gender 파티를 만들 수 없다.
        if current_user.gender == Gender.NONE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="성별이 설정된 사용자만 동성 매칭 파티를 만들 수 있습니다.",
            )
        party_gender = current_user.gender

    fare = estimate_fare(payload.start_lat, payload.start_lng, payload.end_lat, payload.end_lng)

    new_party = Party(
        creator_id=current_user.id,
        start_place=payload.start_place,
        start_lat=payload.start_lat,
        start_lng=payload.start_lng,
        end_place=payload.end_place,
        end_lat=payload.end_lat,
        end_lng=payload.end_lng,
        departure_time=departure,
        meeting_point=payload.meeting_point,
        meeting_note=payload.meeting_note,
        max_members=payload.max_members,
        gender_rule=payload.gender_rule,
        party_gender=party_gender,
        estimated_fare=fare.estimated_fare,
        toll_fare=fare.toll_fare,
        distance_meters=fare.distance_meters,
        duration_seconds=fare.duration_seconds,
        fare_source=fare.fare_source,
        status=PartyStatus.RECRUITING,
    )
    db.add(new_party)
    db.flush()

    db.add(PartyMember(party_id=new_party.id, user_id=current_user.id))
    db.commit()

    return to_detail(_load_party_with_relations(db, new_party.id))


@router.get("", response_model=PartyListResponse)
def list_parties(
    status_filter: PartyStatusType | None = Query(
        default=None, alias="status", description="필터링할 상태값. 미지정 시 recruiting."
    ),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 목록 조회 — 명세서 v0.4 F-PARTY-002.

    기본값은 status=recruiting + departure_time이 미래인 파티만 노출 (F-PARTY-012).
    """
    target_status = status_filter or PartyStatus.RECRUITING

    base_stmt = select(Party).where(Party.status == target_status)
    if target_status == PartyStatus.RECRUITING:
        base_stmt = base_stmt.where(Party.departure_time > now_kst_naive())

    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    offset = (page - 1) * limit
    stmt = (
        base_stmt.order_by(Party.created_at.desc(), Party.id.desc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Party.members))
    )
    parties = db.execute(stmt).scalars().all()

    return PartyListResponse(
        parties=[to_summary(p) for p in parties],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/search", response_model=PartyListResponse)
def search_parties(
    start_place: str | None = Query(default=None, description="출발지명 부분 일치"),
    end_place: str | None = Query(default=None, description="도착지명 부분 일치"),
    departure_time: str | None = Query(
        default=None, description="희망 출발 시간 (ISO 8601). 이후 시각 파티만 검색."
    ),
    status_filter: PartyStatusType | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 검색 — 명세서 v0.4 F-PARTY-007.

    출발지·도착지·희망 시간·상태 기준 부분 일치 검색.
    기본은 recruiting + departure_time 현재 이후 파티만 노출.
    """
    target_status = status_filter or PartyStatus.RECRUITING
    base_stmt = select(Party).where(Party.status == target_status)

    if start_place:
        base_stmt = base_stmt.where(Party.start_place.contains(start_place))
    if end_place:
        base_stmt = base_stmt.where(Party.end_place.contains(end_place))
    if departure_time:
        try:
            from datetime import datetime as dt
            target_time = to_kst_naive(dt.fromisoformat(departure_time))
            base_stmt = base_stmt.where(Party.departure_time >= target_time)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="departure_time 값 형식이 올바르지 않습니다.",
            )
    elif target_status == PartyStatus.RECRUITING:
        base_stmt = base_stmt.where(Party.departure_time > now_kst_naive())

    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    offset = (page - 1) * limit
    stmt = (
        base_stmt.order_by(Party.departure_time.asc(), Party.id.asc())
        .offset(offset)
        .limit(limit)
        .options(selectinload(Party.members))
    )
    parties = db.execute(stmt).scalars().all()

    return PartyListResponse(
        parties=[to_summary(p) for p in parties],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/recommend", response_model=RecommendResponse)
def recommend_parties(
    start_place: str = Query(..., description="원하는 출발지명"),
    end_place: str = Query(..., description="원하는 도착지명"),
    departure_time: str = Query(..., description="원하는 출발 시간 (ISO 8601)"),
    time_range_minutes: int = Query(default=30, ge=1, le=240),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """유사 파티 추천 — 명세서 v0.4 F-PARTY-008 / 알고리즘 설계서 v0.4.

    점수표 (최대 100점):
      - 출발지 일치: +35
      - 도착지 일치: +35
      - 출발 시간 10분 이내: +30 / 20분 이내: +20 / 30분 이내: +10 (중복 가산 X)
    필터:
      - status=recruiting
      - departure_time이 현재 이후
      - 성별 매칭 조건(같은 same_gender면 사용자 성별 일치)
    """
    try:
        from datetime import datetime as dt
        target_time = to_kst_naive(dt.fromisoformat(departure_time))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="departure_time 값 형식이 올바르지 않습니다.",
        )

    window = timedelta(minutes=time_range_minutes)
    window_start = target_time - window
    window_end = target_time + window

    base_stmt = (
        select(Party)
        .where(Party.status == PartyStatus.RECRUITING)
        .where(Party.departure_time > now_kst_naive())
        .where(Party.departure_time >= window_start)
        .where(Party.departure_time <= window_end)
        .options(selectinload(Party.members))
    )
    # 성별 매칭 — same_gender 파티는 사용자 성별과 party_gender가 일치해야 후보
    base_stmt = base_stmt.where(
        or_(
            Party.gender_rule == GenderRule.ANY,
            Party.party_gender == current_user.gender,
        )
    )
    candidates = db.execute(base_stmt).scalars().all()

    scored: list[tuple[int, Party]] = []
    for party in candidates:
        score = 0
        if party.start_place == start_place:
            score += 35
        if party.end_place == end_place:
            score += 35

        dt_diff = abs((to_kst_naive(party.departure_time) - target_time).total_seconds()) / 60
        if dt_diff <= 10:
            score += 30
        elif dt_diff <= 20:
            score += 20
        elif dt_diff <= 30:
            score += 10
        # 30분 초과는 +0

        if score > 0:
            scored.append((score, party))

    scored.sort(key=lambda x: (-x[0], x[1].departure_time))
    top = scored[:limit]

    recommended: list[RecommendedParty] = []
    for score, party in top:
        summary = to_summary(party)
        recommended.append(
            RecommendedParty(
                **summary.model_dump(),
                match_score=score,
                meeting_point=party.meeting_point,
                meeting_note=party.meeting_note,
            )
        )

    return RecommendResponse(parties=recommended)


@router.get("/{party_id}", response_model=PartyDetail)
def get_party_detail(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 상세 조회 — 명세서 v0.4 F-PARTY-003."""
    party = _load_party_with_relations(db, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 파티입니다.")
    return to_detail(party)


@router.post("/{party_id}/join", response_model=PartyDetail)
def join_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 참여 — 명세서 v0.4 F-PARTY-004."""
    party = _load_party_with_relations(db, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 파티입니다.")

    if effective_status(party) != PartyStatus.RECRUITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="모집 중인 파티가 아닙니다.",
        )

    if any(member.user_id == current_user.id for member in party.members):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 참여 중인 파티입니다.",
        )

    # v0.4 신규 검증: 이동 시간대 중복 참여 차단
    if _has_time_conflict(db, current_user.id, party.departure_time, exclude_party_id=party.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="같은 시간대에 이미 참여 중인 파티가 있습니다.",
        )

    if len(party.members) >= party.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 정원이 가득 찬 파티입니다.",
        )

    if party.gender_rule == GenderRule.SAME_GENDER and current_user.gender != party.party_gender:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="동성 매칭 옵션이 설정된 파티로, 참여 조건에 맞지 않습니다.",
        )

    db.add(PartyMember(party_id=party.id, user_id=current_user.id))
    db.flush()
    db.refresh(party)
    sync_status_after_join(party)
    db.commit()

    return to_detail(_load_party_with_relations(db, party.id))


@router.delete("/{party_id}/leave", response_model=PartyDetail)
def leave_party(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 참여 취소 — 명세서 v0.4 F-PARTY-010.

    생성자는 leave 불가 (PATCH /cancel로 파티 자체를 취소해야 함).
    canceled/expired/completed 상태에서는 거부.
    참여자 제거 후 max_members 미만이면 status를 recruiting으로 복귀.
    """
    party = _load_party_with_relations(db, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 파티입니다.")

    if party.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="생성자는 참여 취소할 수 없습니다. 파티 취소를 이용해주세요.",
        )

    if effective_status(party) in {PartyStatus.CANCELED, PartyStatus.EXPIRED, PartyStatus.COMPLETED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="더 이상 참여 취소할 수 없는 파티 상태입니다.",
        )

    membership = next(
        (m for m in party.members if m.user_id == current_user.id), None
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="참여하지 않은 파티입니다.",
        )

    db.delete(membership)
    db.flush()
    db.refresh(party)

    # 인원이 max 미만으로 떨어지면 다시 모집 중으로 복귀 (matched였을 경우)
    if party.status == PartyStatus.MATCHED and len(party.members) < party.max_members:
        party.status = PartyStatus.RECRUITING

    db.commit()
    return to_detail(_load_party_with_relations(db, party.id))


@router.patch("/{party_id}/cancel", response_model=PartyDetail)
def cancel_party(
    party_id: int,
    payload: PartyCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 취소 (생성자) — 명세서 v0.4 F-PARTY-011."""
    party = _load_party_with_relations(db, party_id)
    if party is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 파티입니다.")

    if party.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="파티 생성자만 취소할 수 있습니다.",
        )

    effective = effective_status(party)
    if effective in {PartyStatus.CANCELED, PartyStatus.EXPIRED, PartyStatus.COMPLETED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 종료된 파티는 취소할 수 없습니다.",
        )

    party.status = PartyStatus.CANCELED
    party.cancel_reason = payload.cancel_reason
    party.canceled_at = now_kst_naive()
    db.commit()
    return to_detail(_load_party_with_relations(db, party.id))
