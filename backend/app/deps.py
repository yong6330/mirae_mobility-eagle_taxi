"""공통 FastAPI 의존성 — 라우터에서 `Depends(get_current_user)` 형태로 사용."""

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.constants import UserRole
from app.database import get_db
from app.errors import AppError, ErrorCode
from app.models import User
from app.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def _unauthorized(message: str, error_code: str = ErrorCode.AUTH_REQUIRED) -> AppError:
    return AppError(status.HTTP_401_UNAUTHORIZED, message, error_code)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """JWT를 검증하고 해당 사용자를 반환한다.

    실패 케이스 — 기능명세서 F-AUTH-003:
      · 토큰 없음 → 401 "로그인이 필요합니다."
      · 토큰 만료 → 401 "로그인 정보가 만료되었습니다."
      · 토큰 위조/오류 → 401 "유효하지 않은 토큰입니다."
    """
    if credentials is None or not credentials.credentials:
        raise _unauthorized("로그인이 필요합니다.")

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise _unauthorized("로그인 정보가 만료되었습니다.", ErrorCode.AUTH_TOKEN_EXPIRED)
        raise _unauthorized("유효하지 않은 토큰입니다.", ErrorCode.AUTH_TOKEN_INVALID)

    user_id = payload.get("sub")
    if not user_id:
        raise _unauthorized("유효하지 않은 토큰입니다.", ErrorCode.AUTH_TOKEN_INVALID)

    user = db.get(User, int(user_id))
    if user is None or user.is_deleted:
        raise _unauthorized("유효하지 않은 토큰입니다.", ErrorCode.AUTH_TOKEN_INVALID)
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 검증 — 명세서 v0.4 ADMIN-001~010 공통.

    실패 케이스:
      · 비활성 사용자 → 403 "비활성화된 사용자입니다."
      · 일반 사용자  → 403 "관리자 권한이 필요합니다."
    """
    if not current_user.is_active:
        raise AppError(
            status.HTTP_403_FORBIDDEN, "비활성화된 사용자입니다.", ErrorCode.AUTH_INACTIVE_USER
        )
    if current_user.role != UserRole.ADMIN:
        raise AppError(
            status.HTTP_403_FORBIDDEN, "관리자 권한이 필요합니다.", ErrorCode.ADMIN_REQUIRED
        )
    return current_user


def require_master_admin(current_user: User = Depends(require_admin)) -> User:
    """마스터 관리자 전용 — 명세 §3주차 보완 ADMIN-006(role 변경)에서 사용.

    일반 admin이 시도하면 403 MASTER_ADMIN_REQUIRED.
    """
    if not current_user.master_admin:
        raise AppError(
            status.HTTP_403_FORBIDDEN,
            "마스터 관리자 권한이 필요합니다.",
            ErrorCode.MASTER_ADMIN_REQUIRED,
        )
    return current_user
