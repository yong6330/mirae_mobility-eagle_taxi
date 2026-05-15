"""공통 FastAPI 의존성 — 라우터에서 `Depends(get_current_user)` 형태로 사용."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


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
        message = "로그인 정보가 만료되었습니다." if "expired" in str(exc).lower() else "유효하지 않은 토큰입니다."
        raise _unauthorized(message)

    user_id = payload.get("sub")
    if not user_id:
        raise _unauthorized("유효하지 않은 토큰입니다.")

    user = db.get(User, int(user_id))
    if user is None:
        raise _unauthorized("유효하지 않은 토큰입니다.")
    return user
