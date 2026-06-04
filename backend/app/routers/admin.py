"""관리자 API 라우터 — 명세서 v0.4 ADMIN-001 ~ 010 / F-ADMIN-001 ~ 010.

공통 원칙
  - 모든 엔드포인트는 `require_admin` 의존성으로 보호. 일반 사용자/비활성/미로그인은 모두 403/401.
  - 응답에서 password_hash 등 민감 정보는 노출하지 않는다 (스키마 단계에서 차단).
  - status는 DB 저장값과 effective_status가 다르면 effective_status 기준으로 응답한다.
  - 페이지네이션 기본값: page=1, limit=20 (ADMIN-002 limit=10, ADMIN-008 limit=20).

명세서 8-3 / F-PARTY-006 v0.4 상태값: recruiting / matched / canceled / expired / completed.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.constants import PartyStatus, UserRole
from app.database import get_db
from app.deps import require_admin, require_master_admin
from app.errors import AppError, ErrorCode
from app.models import AdminAction, Message, Party, PartyMember, User
from app.schemas.admin import (
    AdminActionItem,
    AdminActionsResponse,
    AdminPartiesResponse,
    AdminPartyDetailBody,
    AdminPartyDetailResponse,
    AdminPartyItem,
    AdminPartyMemberItem,
    AdminPartyStatusUpdate,
    AdminRecentMessageItem,
    AdminRecentMessagesResponse,
    AdminRecentPartiesResponse,
    AdminStats,
    AdminSystemStatus,
    AdminUserActiveUpdate,
    AdminUserDetail,
    AdminUserDetailResponse,
    AdminUserItem,
    AdminUserRoleUpdate,
    AdminUsersResponse,
)
from app.services.admin_action import AdminActionType, AdminTargetType, log_admin_action
from app.services.fare import per_person_fare
from app.services.party import effective_status
from app.utils.time import KST

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ──────────────────────────────────────────────────────────────
# 내부 헬퍼
# ──────────────────────────────────────────────────────────────


def _to_admin_party_item(party: Party) -> AdminPartyItem:
    """Party 모델을 관리자용 목록 항목으로 변환한다. 시간 만료 status를 반영한다."""
    current = len(party.members)
    return AdminPartyItem(
        id=party.id,
        creator_id=party.creator_id,
        creator_name=party.creator.name if party.creator else "",
        start_place=party.start_place,
        end_place=party.end_place,
        departure_time=party.departure_time,
        current_members=current,
        max_members=party.max_members,
        estimated_fare=party.estimated_fare,
        per_person_fare=per_person_fare(party.estimated_fare, current),
        status=effective_status(party),
        created_at=party.created_at,
    )


def _load_party_for_admin(db: Session, party_id: int) -> Party:
    """파티를 creator·members까지 로드. 없으면 404."""
    stmt = (
        select(Party)
        .where(Party.id == party_id)
        .options(
            selectinload(Party.creator),
            selectinload(Party.members).selectinload(PartyMember.user),
        )
    )
    party = db.execute(stmt).scalar_one_or_none()
    if party is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 파티입니다.",
        )
    return party


def _load_user_for_admin(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise AppError(
            status.HTTP_404_NOT_FOUND, "존재하지 않는 사용자입니다.", ErrorCode.USER_NOT_FOUND
        )
    return user


def _count_active_admins(db: Session) -> int:
    """활성 상태인 admin 수 — 마지막 admin 보호 판정용."""
    return db.execute(
        select(func.count(User.id)).where(
            User.role == UserRole.ADMIN, User.is_active.is_(True)
        )
    ).scalar_one()


# ──────────────────────────────────────────────────────────────
# ADMIN-001: GET /api/admin/stats
# ──────────────────────────────────────────────────────────────


@router.get("/stats", response_model=AdminStats)
def get_stats(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """관리자 통계 조회 — ADMIN-001.

    상태별 파티 수는 DB에 저장된 status 기준으로 집계한다.
    (effective_status는 시간 기반 계산값이지만, 통계는 DB 일관성을 기준으로 본다.)
    """
    total_users = db.execute(select(func.count(User.id))).scalar_one()
    active_users = db.execute(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ).scalar_one()
    total_parties = db.execute(select(func.count(Party.id))).scalar_one()
    total_messages = db.execute(select(func.count(Message.id))).scalar_one()

    status_counts: dict[str, int] = {s: 0 for s in PartyStatus.ALL}
    rows = db.execute(
        select(Party.status, func.count(Party.id)).group_by(Party.status)
    ).all()
    for s, c in rows:
        status_counts[s] = c

    return AdminStats(
        active_users=active_users,
        total_users=total_users,
        total_parties=total_parties,
        recruiting_parties=status_counts[PartyStatus.RECRUITING],
        matched_parties=status_counts[PartyStatus.MATCHED],
        canceled_parties=status_counts[PartyStatus.CANCELED],
        expired_parties=status_counts[PartyStatus.EXPIRED],
        completed_parties=status_counts[PartyStatus.COMPLETED],
        total_messages=total_messages,
    )


# ──────────────────────────────────────────────────────────────
# ADMIN-002: GET /api/admin/parties/recent
# ──────────────────────────────────────────────────────────────


@router.get("/parties/recent", response_model=AdminRecentPartiesResponse)
def get_recent_parties(
    limit: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """최근 생성된 파티 목록 — ADMIN-002. created_at 내림차순."""
    stmt = (
        select(Party)
        .options(
            selectinload(Party.creator),
            selectinload(Party.members),
        )
        .order_by(desc(Party.created_at), desc(Party.id))
        .limit(limit)
    )
    parties = db.execute(stmt).scalars().all()
    return AdminRecentPartiesResponse(items=[_to_admin_party_item(p) for p in parties])


# ──────────────────────────────────────────────────────────────
# ADMIN-003: GET /api/admin/users
# ──────────────────────────────────────────────────────────────


@router.get("/users", response_model=AdminUsersResponse)
def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """사용자 목록 — ADMIN-003. password_hash 노출 금지."""
    total = db.execute(select(func.count(User.id))).scalar_one()
    offset = (page - 1) * limit
    stmt = select(User).order_by(desc(User.created_at), desc(User.id)).offset(offset).limit(limit)
    users = db.execute(stmt).scalars().all()
    return AdminUsersResponse(
        items=[AdminUserItem.model_validate(u) for u in users],
        total=total,
        page=page,
        limit=limit,
    )


# ──────────────────────────────────────────────────────────────
# ADMIN-004: GET /api/admin/parties
# ──────────────────────────────────────────────────────────────


@router.get("/parties", response_model=AdminPartiesResponse)
def list_parties(
    status_filter: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """파티 목록(관리자) — ADMIN-004.

    필터:
      · status — 명세 허용값(recruiting/matched/canceled/expired/completed).
      · keyword — 출발지/도착지/생성자명 LIKE 검색.
    """
    if status_filter is not None and status_filter not in PartyStatus.ALL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="상태값이 올바르지 않습니다.",
        )

    base = select(Party).join(User, Party.creator_id == User.id)
    count_base = select(func.count(Party.id)).join(User, Party.creator_id == User.id)

    if status_filter is not None:
        base = base.where(Party.status == status_filter)
        count_base = count_base.where(Party.status == status_filter)

    if keyword:
        like = f"%{keyword}%"
        cond = or_(
            Party.start_place.like(like),
            Party.end_place.like(like),
            User.name.like(like),
        )
        base = base.where(cond)
        count_base = count_base.where(cond)

    total = db.execute(count_base).scalar_one()
    offset = (page - 1) * limit
    stmt = (
        base.options(selectinload(Party.creator), selectinload(Party.members))
        .order_by(desc(Party.created_at), desc(Party.id))
        .offset(offset)
        .limit(limit)
    )
    parties = db.execute(stmt).scalars().all()
    return AdminPartiesResponse(
        items=[_to_admin_party_item(p) for p in parties],
        total=total,
        page=page,
        limit=limit,
    )


# ──────────────────────────────────────────────────────────────
# ADMIN-005: PATCH /api/admin/parties/{party_id}/status
# ──────────────────────────────────────────────────────────────


@router.patch("/parties/{party_id}/status", response_model=AdminPartyItem)
def update_party_status(
    party_id: int,
    payload: AdminPartyStatusUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """파티 상태 변경 — ADMIN-005.

    payload.status는 PartyStatusType Literal로 이미 검증됨.
    admin_note는 cancel_reason 컬럼에 기록한다 (별도 컬럼 신설 회피).
    변경 이력은 admin_actions에 기록한다 (ADMIN-012).
    """
    party = _load_party_for_admin(db, party_id)
    before_status = party.status
    party.status = payload.status
    if payload.admin_note:
        party.cancel_reason = payload.admin_note
    log_admin_action(
        db,
        actor_admin_id=current_admin.id,
        action_type=AdminActionType.PARTY_STATUS_UPDATE,
        target_type=AdminTargetType.PARTY,
        target_id=party_id,
        before_value=before_status,
        after_value=payload.status,
        note=payload.admin_note,
    )
    db.commit()
    db.refresh(party)
    # 관계 재로드
    party = _load_party_for_admin(db, party_id)
    return _to_admin_party_item(party)


# ──────────────────────────────────────────────────────────────
# ADMIN-006: PATCH /api/admin/users/{user_id}/role
# ──────────────────────────────────────────────────────────────


@router.patch("/users/{user_id}/role", response_model=AdminUserItem)
def update_user_role(
    user_id: int,
    payload: AdminUserRoleUpdate,
    current_admin: User = Depends(require_master_admin),
    db: Session = Depends(get_db),
):
    """사용자 권한 변경 — ADMIN-006.

    명세 §3주차 보완:
      · 마스터 관리자만 호출 가능 (일반 admin은 require_master_admin에서 403).
      · 마스터 관리자 대상 role 변경은 409 MASTER_ADMIN_PROTECTED.
      · 마지막 활성 admin 강등은 409 LAST_ADMIN_CANNOT_BE_DEMOTED.
    변경 이력은 admin_actions에 기록한다.
    """
    user = _load_user_for_admin(db, user_id)

    if user.master_admin:
        raise AppError(
            status.HTTP_409_CONFLICT,
            "마스터 관리자의 권한은 변경할 수 없습니다.",
            ErrorCode.MASTER_ADMIN_PROTECTED,
        )
    if (
        user.role == UserRole.ADMIN
        and payload.role == UserRole.USER
        and user.is_active
        and _count_active_admins(db) <= 1
    ):
        raise AppError(
            status.HTTP_409_CONFLICT,
            "마지막 활성 관리자는 강등할 수 없습니다.",
            ErrorCode.LAST_ADMIN_CANNOT_BE_DEMOTED,
        )

    before_role = user.role
    user.role = payload.role
    log_admin_action(
        db,
        actor_admin_id=current_admin.id,
        action_type=AdminActionType.USER_ROLE_UPDATE,
        target_type=AdminTargetType.USER,
        target_id=user_id,
        before_value=before_role,
        after_value=payload.role,
    )
    db.commit()
    db.refresh(user)
    return AdminUserItem.model_validate(user)


# ──────────────────────────────────────────────────────────────
# ADMIN-007: PATCH /api/admin/users/{user_id}/status
# (명세서: 활성 상태 변경 — endpoint는 /status, body는 is_active)
# ──────────────────────────────────────────────────────────────


@router.patch("/users/{user_id}/status", response_model=AdminUserItem)
def update_user_active(
    user_id: int,
    payload: AdminUserActiveUpdate,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """사용자 활성 상태 변경 — ADMIN-007. 변경 이력은 admin_actions에 기록한다.

    명세 §3주차 보완: 마스터 관리자 비활성화와 마지막 활성 admin 비활성화는 409.
    is_active=false로 바꾸면 로그인/주요 기능 이용이 차단된다 (auth.py에서 401/403).
    """
    user = _load_user_for_admin(db, user_id)

    if payload.is_active is False:
        if user.master_admin:
            raise AppError(
                status.HTTP_409_CONFLICT,
                "마스터 관리자는 비활성화할 수 없습니다.",
                ErrorCode.MASTER_ADMIN_PROTECTED,
            )
        if user.role == UserRole.ADMIN and user.is_active and _count_active_admins(db) <= 1:
            raise AppError(
                status.HTTP_409_CONFLICT,
                "마지막 활성 관리자는 비활성화할 수 없습니다.",
                ErrorCode.LAST_ADMIN_CANNOT_BE_DEACTIVATED,
            )

    before_active = str(user.is_active)
    user.is_active = payload.is_active
    log_admin_action(
        db,
        actor_admin_id=current_admin.id,
        action_type=AdminActionType.USER_STATUS_UPDATE,
        target_type=AdminTargetType.USER,
        target_id=user_id,
        before_value=before_active,
        after_value=str(payload.is_active),
    )
    db.commit()
    db.refresh(user)
    return AdminUserItem.model_validate(user)


# ──────────────────────────────────────────────────────────────
# ADMIN-008: GET /api/admin/messages/recent
# ──────────────────────────────────────────────────────────────


@router.get("/messages/recent", response_model=AdminRecentMessagesResponse)
def get_recent_messages(
    limit: int = Query(default=20, ge=1, le=200),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """최근 채팅 메시지(관리자 모니터링) — ADMIN-008. 읽기 전용."""
    stmt = (
        select(Message)
        .options(selectinload(Message.user))
        .order_by(desc(Message.created_at), desc(Message.id))
        .limit(limit)
    )
    messages = db.execute(stmt).scalars().all()
    items = [
        AdminRecentMessageItem(
            id=m.id,
            party_id=m.party_id,
            user_id=m.user_id,
            user_name=m.user.name if m.user else "",
            content=m.content,
            created_at=m.created_at,
        )
        for m in messages
    ]
    return AdminRecentMessagesResponse(recent_messages=items)


# ──────────────────────────────────────────────────────────────
# ADMIN-009: GET /api/admin/users/{user_id}
# ──────────────────────────────────────────────────────────────


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
def get_user_detail(
    user_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """사용자 상세 — ADMIN-009. 생성/참여 파티 카운트 + 메시지 카운트 포함."""
    user = _load_user_for_admin(db, user_id)

    created_count = db.execute(
        select(func.count(Party.id)).where(Party.creator_id == user_id)
    ).scalar_one()
    joined_count = db.execute(
        select(func.count(PartyMember.id)).where(PartyMember.user_id == user_id)
    ).scalar_one()
    message_count = db.execute(
        select(func.count(Message.id)).where(Message.user_id == user_id)
    ).scalar_one()

    return AdminUserDetailResponse(
        user=AdminUserDetail.model_validate(user),
        created_parties_count=created_count,
        joined_parties_count=joined_count,
        message_count=message_count,
    )


# ──────────────────────────────────────────────────────────────
# ADMIN-010: GET /api/admin/parties/{party_id}
# ──────────────────────────────────────────────────────────────


@router.get("/parties/{party_id}", response_model=AdminPartyDetailResponse)
def get_party_detail(
    party_id: int,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """파티 상세(관리자) — ADMIN-010. 상태 변경은 ADMIN-005를 사용."""
    party = _load_party_for_admin(db, party_id)
    current = len(party.members)

    messages_count = db.execute(
        select(func.count(Message.id)).where(Message.party_id == party_id)
    ).scalar_one()

    members = [
        AdminPartyMemberItem(id=m.user.id, name=m.user.name, gender=m.user.gender)
        for m in party.members
    ]

    return AdminPartyDetailResponse(
        party=AdminPartyDetailBody(
            id=party.id,
            start_place=party.start_place,
            end_place=party.end_place,
            status=effective_status(party),
            current_members=current,
            max_members=party.max_members,
        ),
        members=members,
        messages_count=messages_count,
    )


# ──────────────────────────────────────────────────────────────
# ADMIN-011: GET /api/admin/system/status
# ──────────────────────────────────────────────────────────────


@router.get("/system/status", response_model=AdminSystemStatus)
def get_system_status(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """관리자 시스템 상태 조회 — ADMIN-011.

    서버/DB/Kakao 설정/fallback 옵션/서버 시간을 읽기 전용으로 반환한다.
    """
    try:
        db.execute(select(1))
        db_status = "ok"
    except Exception:  # noqa: BLE001 — 상태 보고용이므로 어떤 DB 오류든 error로 표기
        db_status = "error"

    return AdminSystemStatus(
        api_status="ok",
        db_status=db_status,
        kakao_mobility_configured=bool(settings.kakao_rest_api_key),
        fare_fallback_enabled=settings.allow_fare_fallback,
        server_time=datetime.now(KST),
    )


# ──────────────────────────────────────────────────────────────
# ADMIN-012: GET /api/admin/actions
# ──────────────────────────────────────────────────────────────


@router.get("/actions", response_model=AdminActionsResponse)
def get_admin_actions(
    action_type: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """관리자 조작 기록 조회 — ADMIN-012.

    role 변경/사용자 활성 변경/파티 상태 변경 이력을 최신순으로 조회한다.
    필터: action_type, target_type (선택).
    """
    count_base = select(func.count(AdminAction.id))
    base = select(AdminAction)

    if action_type:
        base = base.where(AdminAction.action_type == action_type)
        count_base = count_base.where(AdminAction.action_type == action_type)
    if target_type:
        base = base.where(AdminAction.target_type == target_type)
        count_base = count_base.where(AdminAction.target_type == target_type)

    total = db.execute(count_base).scalar_one()
    offset = (page - 1) * limit
    stmt = (
        base.options(selectinload(AdminAction.actor))
        .order_by(desc(AdminAction.created_at), desc(AdminAction.id))
        .offset(offset)
        .limit(limit)
    )
    rows = db.execute(stmt).scalars().all()
    items = [
        AdminActionItem(
            id=a.id,
            actor_admin_id=a.actor_admin_id,
            actor_admin_name=a.actor.name if a.actor else "",
            action_type=a.action_type,
            target_type=a.target_type,
            target_id=a.target_id,
            before_value=a.before_value,
            after_value=a.after_value,
            note=a.note,
            created_at=a.created_at,
        )
        for a in rows
    ]
    return AdminActionsResponse(items=items, total=total, page=page, limit=limit)
