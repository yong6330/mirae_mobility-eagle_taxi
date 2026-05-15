"""Pydantic 검증 오류를 명세서 형식(400 + 한글 메시지)으로 변환한다.

기능명세서 F-AUTH-001 등에서 다음과 같은 한글 예외 메시지를 요구한다:
  · 필수값 누락 → "필수 항목을 입력해주세요."
  · 이메일 형식 오류 → "이메일 형식에 맞춰 입력해주세요."
  · 성별값 오류 → "성별 값이 올바르지 않습니다."

FastAPI 기본 동작은 422 + 영문 구조화 에러이므로, 글로벌 핸들러로 변환한다.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _korean_message_for(error: dict) -> str:
    """첫 번째 Pydantic 에러 한 건을 한글 메시지로 매핑한다."""
    error_type = error.get("type", "")
    loc = error.get("loc", [])
    field = str(loc[-1]) if loc else ""
    msg_lower = error.get("msg", "").lower()

    # 필수값 누락 (Body 자체 부재 포함)
    if error_type == "missing":
        return "필수 항목을 입력해주세요."

    # 이메일 형식 오류
    if "email" in msg_lower or field == "email":
        return "이메일 형식에 맞춰 입력해주세요."

    # 문자열 길이 (비밀번호 / 이름 등)
    if error_type in ("string_too_short", "string_too_long"):
        if field == "password":
            return "비밀번호 형식이 올바르지 않습니다."
        if field == "name":
            return "이름을 입력해주세요."
        return "입력값 길이가 올바르지 않습니다."

    # Literal 값 (gender / gender_rule / status)
    if error_type == "literal_error":
        if field == "gender":
            return "성별 값이 올바르지 않습니다."
        if field == "gender_rule":
            return "성별 매칭 옵션이 올바르지 않습니다."
        if field == "status":
            return "상태값이 올바르지 않습니다."
        return "허용되지 않는 값입니다."

    # 숫자 범위 (max_members 2~4 등)
    if error_type in ("greater_than_equal", "less_than_equal", "greater_than", "less_than"):
        if field == "max_members":
            return "최대 인원은 2명에서 4명 사이여야 합니다."
        return "입력값 범위가 올바르지 않습니다."

    # 타입 오류 (숫자 자리에 문자열 등)
    if error_type in ("int_parsing", "float_parsing", "datetime_parsing", "type_error"):
        return f"{field} 값 형식이 올바르지 않습니다." if field else "입력값 형식이 올바르지 않습니다."

    return "입력값이 올바르지 않습니다."


def _serialize_errors(errors: list[dict]) -> list[dict]:
    """디버깅용 — 원본 에러를 단순화해서 함께 내려준다."""
    return [
        {
            "field": ".".join(str(part) for part in err.get("loc", []) if part != "body"),
            "type": err.get("type"),
            "msg": err.get("msg"),
        }
        for err in errors
    ]


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Pydantic RequestValidationError → 400 + 한글 detail."""
    errors = exc.errors()
    message = _korean_message_for(errors[0]) if errors else "입력값이 올바르지 않습니다."
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": message, "errors": _serialize_errors(errors)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
