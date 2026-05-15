"""인증 관련 Pydantic 스키마 — 회원가입·로그인·내 정보 조회 요청/응답 정의."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants import Gender, GenderType, UserRoleType


class RegisterRequest(BaseModel):
    """POST /api/auth/register 요청 Body — 기능명세서 F-AUTH-001."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=50)
    gender: GenderType = Gender.NONE


class UserOut(BaseModel):
    """사용자 응답 객체 — 회원가입·내 정보 조회·로그인 응답에서 공통 사용."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    gender: GenderType
    role: UserRoleType
    created_at: datetime


class RegisterResponse(BaseModel):
    """회원가입 응답 — 기능명세서 F-AUTH-001 출력값 "가입 완료 메시지" 포함."""

    message: str = "회원가입이 완료되었습니다."
    user: UserOut


class LoginRequest(BaseModel):
    """POST /api/auth/login 요청 Body — 기능명세서 F-AUTH-002."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """로그인 응답 — access_token + user 정보."""

    access_token: str
    token_type: str = "bearer"
    user: UserOut
