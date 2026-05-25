"""관리자 API 응답/요청 스키마 — 명세서 v0.4 ADMIN-001 ~ 010.

핵심 원칙:
  - password_hash 등 민감 정보는 절대 노출하지 않는다 (ADMIN-003/008/009 주의사항).
  - 사용자/파티 응답은 기존 schemas의 UserOut과 별개로 관리자용 최소 필드만 노출한다.
  - 모든 응답은 from_attributes=True로 ORM 객체에서 변환한다.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import GenderType, PartyStatusType, UserRoleType


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
    """ADMIN-005 요청 Body."""

    status: PartyStatusType
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
