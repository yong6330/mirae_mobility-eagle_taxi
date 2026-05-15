"""인증 라우터 — 기능명세서 F-AUTH-001 ~ 003.

F-AUTH-004(로그아웃)은 백엔드 API 없이 프론트에서 토큰 삭제로 처리한다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.constants import UserRole
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserOut,
)
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _is_admin_email(email: str) -> bool:
    return email in settings.admin_email_set


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """회원가입 — 기능명세서 F-AUTH-001."""
    email = payload.email.lower()

    if db.execute(select(User).where(User.email == email)).scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다.",
        )

    new_user = User(
        email=email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        gender=payload.gender,
        role=UserRole.ADMIN if _is_admin_email(email) else UserRole.USER,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RegisterResponse(user=UserOut.model_validate(new_user))


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """로그인 — 기능명세서 F-AUTH-002.

    이메일·비밀번호 일치 시 JWT access_token을 발급한다.
    실패 시 401 + "이메일 또는 비밀번호가 올바르지 않습니다." (계정 존재 여부 노출 방지)
    """
    email = payload.email.lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",
        )

    return LoginResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """내 정보 조회 — 기능명세서 F-AUTH-003. 토큰 검증은 의존성에서 처리한다."""
    return current_user
