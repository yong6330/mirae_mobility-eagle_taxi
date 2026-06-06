"""비밀번호 해시·JWT 토큰 발급/검증 유틸리티."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings

_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    """평문 비밀번호를 bcrypt 해시로 변환한다."""
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 저장된 해시가 일치하는지 확인한다."""
    try:
        return bcrypt.checkpw(_password_bytes(plain_password), hashed_password.encode("utf-8"))
    except (TypeError, ValueError):
        return False


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def create_access_token(subject: str | int) -> str:
    """JWT access token 발급. subject에는 보통 user.id를 넣는다."""
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_minutes)
    payload = {"sub": str(subject), "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """JWT 토큰을 디코드해서 payload를 반환한다. 만료/위조 시 JWTError를 던진다."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
