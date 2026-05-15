"""파티 라우터 — 기능명세서 F-PARTY-001 ~ 004."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.constants import Gender, GenderRule, PartyStatus, PartyStatusType
from app.database import get_db
from app.deps import get_current_user
from app.models import Party, PartyMember, User
from app.schemas.party import (
    PartyCreateRequest,
    PartyDetail,
    PartyListResponse,
)
from app.services.fare import estimate_fare
from app.services.party import effective_status, sync_status_after_join, to_detail, to_summary
from app.utils.time import now_kst_naive, to_kst_naive

router = APIRouter(prefix="/api/parties", tags=["parties"])


def _load_party_with_relations(db: Session, party_id: int) -> Party | None:
    """파티를 members·creator·users 관계까지 한 번에 로드한다 (N+1 방지)."""
    stmt = (
        select(Party)
        .where(Party.id == party_id)
        .options(
            selectinload(Party.creator),
            selectinload(Party.members).selectinload(PartyMember.user),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


@router.post("", response_model=PartyDetail, status_code=status.HTTP_201_CREATED)
def create_party(
    payload: PartyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 생성 — 기능명세서 F-PARTY-001.

    추가 검증 (Pydantic 외):
      · 출발 시간이 현재 이후여야 한다 (KST 기준)
      · same_gender 옵션은 생성자 gender=none이면 거부 (F-PARTY-013)
    """
    departure = to_kst_naive(payload.departure_time)
    if departure <= now_kst_naive():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="출발 시간은 현재 시각 이후여야 합니다.",
        )

    party_gender: str | None = None
    if payload.gender_rule == GenderRule.SAME_GENDER:
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
    """파티 목록 조회 — 기능명세서 F-PARTY-002.

    기본값은 status=recruiting + departure_time이 미래인 파티만 노출 (F-PARTY-011).
    """
    target_status = status_filter or PartyStatus.RECRUITING

    base_stmt = select(Party).where(Party.status == target_status)
    if target_status == PartyStatus.RECRUITING:
        base_stmt = base_stmt.where(Party.departure_time > now_kst_naive())

    total = db.execute(select(func.count()).select_from(base_stmt.subquery())).scalar_one()

    offset = (page - 1) * limit
    stmt = (
        base_stmt.order_by(Party.created_at.desc())
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


@router.get("/{party_id}", response_model=PartyDetail)
def get_party_detail(
    party_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """파티 상세 조회 — 기능명세서 F-PARTY-003."""
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
    """파티 참여 — 기능명세서 F-PARTY-004."""
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
