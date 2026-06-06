"""관리자 API 응답/요청 스키마 — 명세서 v0.4 ADMIN-001 ~ 010.

핵심 원칙:
  - password_hash 등 민감 정보는 절대 노출하지 않는다 (ADMIN-003/008/009 주의사항).
  - 사용자/파티 응답은 기존 schemas의 UserOut과 별개로 관리자용 최소 필드만 노출한다.
  - 모든 응답은 from_attributes=True로 ORM 객체에서 변환한다.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import GenderRuleType, GenderType, PartyStatusType, UserRoleType
from app.schemas.party import PartyDetail


# ──────────────────────────────────────────────────────────────
# ADMIN-001: 통계
# ──────────────────────────────────────────────────────────────


class AdminStats(BaseModel):
    """GET /api/admin/stats 응답 — ADMIN-001."""

    active_users: int
    total_users: int
    total_parties: int
    recruiting_parties: int
    matched_parties: int
    canceled_parties: int
    expired_parties: int
    completed_parties: int
    total_messages: int


# ──────────────────────────────────────────────────────────────
# ADMIN-002, ADMIN-004: 파티 요약 (관리자 시점)
# ──────────────────────────────────────────────────────────────


class AdminPartyItem(BaseModel):
    """관리자 파티 목록 항목 — ADMIN-002 / ADMIN-004 공통.

    creator_name은 ADMIN-004 응답에만 포함되지만, 공통 스키마로 두고
    ADMIN-002 응답에서도 같이 내려준다 (정보량 증가 방향이라 안전).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    creator_id: int
    creator_name: str
    start_place: str
    end_place: str
    departure_time: datetime
    current_members: int
    max_members: int
    estimated_fare: int
    per_person_fare: int
    status: PartyStatusType
    created_at: datetime


class AdminRecentPartiesResponse(BaseModel):
    """ADMIN-002 응답."""

    items: list[AdminPartyItem]


class AdminPartiesResponse(BaseModel):
    """ADMIN-004 응답 — 페이지네이션 포함."""

    items: list[AdminPartyItem]
    total: int
    page: int
    limit: int


# ──────────────────────────────────────────────────────────────
# ADMIN-003: 사용자 목록
# ──────────────────────────────────────────────────────────────


class AdminUserItem(BaseModel):
    """관리자 사용자 목록 항목 — ADMIN-003.

    password_hash 절대 노출 금지.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    gender: GenderType
    role: UserRoleType
    is_active: bool
    master_admin: bool = False
    is_deleted: bool = False
    deleted_at: datetime | None = None
    created_at: datetime


class AdminUsersResponse(BaseModel):
    """ADMIN-003 응답."""

    items: list[AdminUserItem]
    total: int
    page: int
    limit: int


# ──────────────────────────────────────────────────────────────
# ADMIN-005: 파티 상태 변경
# ──────────────────────────────────────────────────────────────


class AdminPartyStatusUpdate(BaseModel):
    """ADMIN-005 / ADMIN-021 요청 Body. force는 master admin의 matched 인원조건 우회용."""

    status: PartyStatusType
    force: bool = False
    admin_note: str | None = Field(default=None, max_length=500)


# ──────────────────────────────────────────────────────────────
# ADMIN-006: 사용자 권한 변경
# ──────────────────────────────────────────────────────────────


class AdminUserRoleUpdate(BaseModel):
    """ADMIN-006 요청 Body."""

    role: UserRoleType


# ──────────────────────────────────────────────────────────────
# ADMIN-007: 사용자 활성 상태 변경
# ──────────────────────────────────────────────────────────────


class AdminUserActiveUpdate(BaseModel):
    """ADMIN-007 요청 Body."""

    is_active: bool


# ──────────────────────────────────────────────────────────────
# ADMIN-008: 최근 메시지
# ──────────────────────────────────────────────────────────────


class AdminRecentMessageItem(BaseModel):
    """ADMIN-008 응답 항목."""

    id: int
    party_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime


class AdminRecentMessagesResponse(BaseModel):
    """ADMIN-008 응답 — 응답 필드명은 명세서 그대로 `recent_messages`."""

    recent_messages: list[AdminRecentMessageItem]


# ──────────────────────────────────────────────────────────────
# ADMIN-009: 사용자 상세
# ──────────────────────────────────────────────────────────────


class AdminUserDetail(BaseModel):
    """ADMIN-009 응답 내부 user 객체."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    gender: GenderType
    role: UserRoleType
    is_active: bool
    master_admin: bool = False
    created_at: datetime


class AdminUserDetailResponse(BaseModel):
    """ADMIN-009 응답 전체."""

    user: AdminUserDetail
    created_parties_count: int
    joined_parties_count: int
    message_count: int


# ──────────────────────────────────────────────────────────────
# ADMIN-010: 파티 상세
# ──────────────────────────────────────────────────────────────


class AdminPartyMemberItem(BaseModel):
    """ADMIN-010 응답의 members 항목."""

    id: int
    name: str
    gender: GenderType


class AdminPartyDetailBody(BaseModel):
    """ADMIN-010 응답 내부 party 객체."""

    id: int
    start_place: str
    end_place: str
    status: PartyStatusType
    current_members: int
    max_members: int


class AdminPartyDetailResponse(BaseModel):
    """ADMIN-010 응답 전체."""

    party: AdminPartyDetailBody
    members: list[AdminPartyMemberItem]
    messages_count: int


# ──────────────────────────────────────────────────────────────
# ADMIN-011: 시스템 상태 조회
# ──────────────────────────────────────────────────────────────


class AdminSystemStatus(BaseModel):
    """GET /api/admin/system/status 응답 — ADMIN-011."""

    api_status: str
    db_status: str
    mobility_provider_configured: bool
    fare_fallback_enabled: bool
    server_time: datetime


# ──────────────────────────────────────────────────────────────
# ADMIN-012: 관리자 조작 기록 조회
# ──────────────────────────────────────────────────────────────


class AdminActionItem(BaseModel):
    """ADMIN-012 응답 항목."""

    id: int
    actor_admin_id: int
    actor_admin_name: str
    action_type: str
    target_type: str
    target_id: int
    before_value: str | None
    after_value: str | None
    note: str | None
    created_at: datetime


class AdminActionsResponse(BaseModel):
    """ADMIN-012 응답 — 페이지네이션 포함."""

    items: list[AdminActionItem]
    total: int
    page: int
    limit: int


# ──────────────────────────────────────────────────────────────
# ADMIN-013~016: 사용자 유지보수 (생성/수정/비번초기화/삭제)
# ──────────────────────────────────────────────────────────────


class AdminUserCreate(BaseModel):
    """ADMIN-013 요청 Body."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=50)
    gender: Literal["male", "female"]  # v0.4 저장값은 male/female만
    role: UserRoleType = "user"
    is_active: bool = True
    admin_note: str | None = None


class AdminUserUpdate(BaseModel):
    """ADMIN-014 요청 Body — 부분 수정. 보낸 필드만 변경."""

    email: EmailStr | None = None
    name: str | None = Field(default=None, max_length=50)
    gender: Literal["male", "female"] | None = None
    role: UserRoleType | None = None
    is_active: bool | None = None
    admin_note: str | None = None


class AdminPasswordReset(BaseModel):
    """ADMIN-015 요청 Body."""

    new_password: str
    force_logout: bool = False
    admin_note: str | None = None


class AdminUserDelete(BaseModel):
    """ADMIN-016 요청 Body."""

    delete_mode: str = "soft"
    admin_note: str | None = None


class AdminUserMutationResponse(BaseModel):
    """ADMIN-013/014 응답 — 변경된 사용자 + 감사로그 ID."""

    user: AdminUserItem
    admin_action_id: int


class AdminPasswordResetResponse(BaseModel):
    """ADMIN-015 응답."""

    password_reset: bool
    force_logout_applied: bool
    admin_action_id: int


class AdminUserDeleteResponse(BaseModel):
    """ADMIN-016 응답."""

    deleted: bool
    admin_action_id: int


# ──────────────────────────────────────────────────────────────
# ADMIN-018~023: 파티 유지보수 (생성/수정/삭제/참여자)
# ──────────────────────────────────────────────────────────────


class AdminPartyCreate(BaseModel):
    """ADMIN-018 요청 Body."""

    creator_user_id: int
    start_place: str
    start_lat: float
    start_lng: float
    end_place: str
    end_lat: float
    end_lng: float
    departure_time: datetime
    meeting_point: str | None = None
    meeting_note: str | None = None
    max_members: int = 4
    gender_rule: GenderRuleType = "any"
    initial_member_ids: list[int] = Field(default_factory=list)
    status: Literal["recruiting", "matched"] = "recruiting"
    force: bool = False
    admin_note: str | None = None


class AdminPartyUpdate(BaseModel):
    """ADMIN-019 요청 Body — 부분 수정."""

    creator_user_id: int | None = None
    start_place: str | None = None
    start_lat: float | None = None
    start_lng: float | None = None
    end_place: str | None = None
    end_lat: float | None = None
    end_lng: float | None = None
    departure_time: datetime | None = None
    meeting_point: str | None = None
    meeting_note: str | None = None
    max_members: int | None = None
    gender_rule: GenderRuleType | None = None
    recalculate_fare: bool = False
    force: bool = False
    admin_note: str | None = None


class AdminPartyDelete(BaseModel):
    """ADMIN-020 요청 Body."""

    delete_mode: str = "soft"
    admin_note: str | None = None


class AdminMemberAdd(BaseModel):
    """ADMIN-022 요청 Body."""

    user_id: int
    force: bool = False
    admin_note: str | None = None


class AdminMemberRemove(BaseModel):
    """ADMIN-023 요청 Body."""

    admin_note: str | None = None


class AdminPartyMutationResponse(BaseModel):
    """ADMIN-018/019/022/023 응답 — 변경된 파티 상세 + 감사로그 ID."""

    party: PartyDetail
    admin_action_id: int


class AdminPartyDeleteResponse(BaseModel):
    """ADMIN-020 응답."""

    deleted: bool
    admin_action_id: int


# ──────────────────────────────────────────────────────────────
# ADMIN-017 / 024 / 025 / 026 / 027 (P1)
# ──────────────────────────────────────────────────────────────


class AdminUserPartyItem(BaseModel):
    """ADMIN-017 응답 항목."""

    party_id: int
    relation: str  # created / joined
    status: PartyStatusType
    start_place: str
    end_place: str
    departure_time: datetime
    current_members: int
    max_members: int


class AdminUserPartiesResponse(BaseModel):
    """ADMIN-017 응답."""

    items: list[AdminUserPartyItem]
    total: int
    page: int
    limit: int


class AdminFareRecalculate(BaseModel):
    """ADMIN-024 요청 Body."""

    admin_note: str | None = None


class AdminFareOverride(BaseModel):
    """ADMIN-025 요청 Body."""

    estimated_fare: int = Field(ge=0)
    toll_fare: int = Field(default=0, ge=0)
    distance_meters: int = Field(ge=0)
    duration_seconds: int = Field(ge=0)
    fare_source: str = "admin_override"
    admin_note: str | None = None


class AdminMessageHide(BaseModel):
    """ADMIN-026 요청 Body."""

    admin_note: str | None = None


class AdminMessageHideResponse(BaseModel):
    """ADMIN-026 응답."""

    hidden: bool
    admin_action_id: int


class AdminNoticeCreate(BaseModel):
    """ADMIN-027 요청 Body."""

    content: str = Field(min_length=1, max_length=1000)
    admin_note: str | None = None


class AdminNoticeMessageOut(BaseModel):
    """ADMIN-027 응답의 message 객체."""

    id: int
    party_id: int
    content: str
    is_admin_notice: bool
    created_at: datetime


class AdminNoticeResponse(BaseModel):
    """ADMIN-027 응답."""

    message: AdminNoticeMessageOut
    admin_action_id: int
