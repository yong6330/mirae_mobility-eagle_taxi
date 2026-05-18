"""인증 관련 Pydantic 스키마 — 명세서 v0.4 기준.

핵심 변경 (v0.4):
- 회원가입 응답은 user 객체를 직접 반환 (message wrapper 제거)
- gender는 male/female 두 값만 허용 (none은 회원가입 단계에서 거부)
- 응답에 is_active 포함
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import GenderType, UserRoleType

# 회원가입에서만 허용하는 성별 (none 제외) — 명세서 v0.4 AUTH-001
RegisterGender = Literal["male", "female"]


class RegisterRequest(BaseModel):
    """POST /api/auth/register 요청 Body — 기능명세서 v0.4 F-AUTH-001."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=50)
    gender: RegisterGender  # 기본값 제거 — 필수 입력


class UserOut(BaseModel):
    """사용자 응답 객체 — 명세서 v0.4 AUTH-001/AUTH-003/F-ACCOUNT-001 응답 형식.

    필드: id, email, name, gender, role, is_active, created_at.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    gender: GenderType
    role: UserRoleType
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    """POST /api/auth/login 요청 Body — 기능명세서 v0.4 F-AUTH-002."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """로그인 응답 — access_token + user 정보."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
