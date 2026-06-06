"""인증 라우터 — 명세서 v0.4 F-AUTH-001 ~ 003.

F-AUTH-004(로그아웃)은 백엔드 API 없이 프론트에서 토큰 삭제로 처리한다.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.constants import UserRole
from app.database import get_db
from app.deps import get_current_user
from app.errors import AppError, ErrorCode
from app.models import User
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserOut
from app.security import create_access_token, hash_password, verify_password
from app.services.admin_action import AdminActionType, AdminTargetType, log_admin_action

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _is_admin_email(email: str) -> bool:
    return email in settings.admin_email_set


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """회원가입 — 명세서 v0.4 F-AUTH-001.

    응답: 생성된 사용자 객체를 직접 반환 (래퍼 없음, 명세 v0.4 AUTH-001).
    gender는 male/female 둘 중 하나 필수, role은 user, is_active는 true가 기본.
    """
    email = payload.email.lower()

    if db.execute(select(User).where(User.email == email)).scalar_one_or_none() is not None:
        raise AppError(
            status.HTTP_409_CONFLICT,
            "이미 가입된 이메일입니다.",
            ErrorCode.AUTH_EMAIL_ALREADY_EXISTS,
        )

    new_user = User(
        email=email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        gender=payload.gender,
        role=UserRole.ADMIN if _is_admin_email(email) else UserRole.USER,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """로그인 — 명세서 v0.4 F-AUTH-002.

    이메일·비밀번호 일치 시 JWT access_token을 발급한다.
    비활성화된 사용자(is_active=False)는 로그인 거부.
    """
    email = payload.email.lower()
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    if user is None or user.is_deleted or not verify_password(payload.password, user.password_hash):
        raise AppError(
            status.HTTP_401_UNAUTHORIZED,
            "이메일 또는 비밀번호가 올바르지 않습니다.",
            ErrorCode.AUTH_INVALID_CREDENTIALS,
        )
    if not user.is_active:
        raise AppError(
            status.HTTP_403_FORBIDDEN,
            "비활성화된 계정입니다. 관리자에게 문의해주세요.",
            ErrorCode.AUTH_INACTIVE_USER,
        )

    if user.role == UserRole.ADMIN:
        log_admin_action(
            db,
            actor_admin_id=user.id,
            action_type=AdminActionType.ADMIN_LOGIN,
            target_type=AdminTargetType.USER,
            target_id=user.id,
            before_value="signed_out",
            after_value="signed_in",
            note="관리자 로그인",
        )
        db.commit()

    return LoginResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """내 정보 조회 — 명세서 v0.4 F-AUTH-003."""
    return current_user
