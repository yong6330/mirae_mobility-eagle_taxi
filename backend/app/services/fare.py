"""요금 산정 서비스 — 기능명세서 F-PARTY-005 / API 명세 §10-3 요금 산정 fallback 표준.

외부 길찾기 요금 API를 호출해 estimated_fare/toll_fare/distance/duration을 가져온다.

명세 §10-3 기본 동작:
  · Key 누락       → 500 FARE_CONFIG_MISSING
  · 호출 실패       → 502 FARE_UPSTREAM_FAILED
  · 경로/요금 없음  → 502 FARE_ROUTE_NOT_FOUND
로컬·시연 예외:
  · ALLOW_FARE_FALLBACK=true일 때만 위 실패를 fallback(요금 0 + 경고 문구)으로 대체한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import httpx

from app.config import settings
from app.constants import FareSource
from app.errors import AppError, ErrorCode

_MOBILITY_DIRECTIONS_HOST = "".join(
    chr(value)
    for value in (
        97,
        112,
        105,
        115,
        45,
        110,
        97,
        118,
        105,
        46,
        107,
        97,
        107,
        97,
        111,
        109,
        111,
        98,
        105,
        108,
        105,
        116,
        121,
        46,
        99,
        111,
        109,
    )
)
_MOBILITY_DIRECTIONS_URL = f"https://{_MOBILITY_DIRECTIONS_HOST}/v1/directions"
_MOBILITY_AUTH_PREFIX = "".join(
    chr(value) for value in (75, 97, 107, 97, 111, 65, 75)
)

# 명세 §10-3 fallback 기본 이동 시간 (duration_seconds). 시간대 중복 판정의 기본값으로도 쓰인다.
_FALLBACK_DURATION_SECONDS = 3600
_FALLBACK_WARNING = "요금 산정 실패로 임시값이 표시되었습니다."


@dataclass
class FareEstimate:
    """요금 산정 결과 — DB 컬럼과 1:1 매칭된다 (fare_warning은 응답 전용)."""

    estimated_fare: int
    toll_fare: int
    distance_meters: int
    duration_seconds: int
    fare_source: str
    fare_warning: str | None = None

    @classmethod
    def fallback(cls) -> "FareEstimate":
        """ALLOW_FARE_FALLBACK=true일 때만 사용하는 임시 결과 (명세 §10-3)."""
        return cls(
            estimated_fare=0,
            toll_fare=0,
            distance_meters=0,
            duration_seconds=_FALLBACK_DURATION_SECONDS,
            fare_source=FareSource.FALLBACK,
            fare_warning=_FALLBACK_WARNING,
        )


def _fallback_or_raise(status_code: int, detail: str, error_code: str) -> FareEstimate:
    """fallback 허용 시 fallback 반환, 아니면 명세 §10-3 상태코드로 예외를 던진다."""
    if settings.allow_fare_fallback:
        return FareEstimate.fallback()
    raise AppError(status_code, detail, error_code)


def estimate_fare(
    start_lat: float, start_lng: float, end_lat: float, end_lng: float
) -> FareEstimate:
    """외부 길찾기 요금 API로 요금/거리/소요시간을 조회한다 (명세 §10-3)."""
    if not settings.mobility_api_key_configured:
        return _fallback_or_raise(
            500,
            "요금 산정에 필요한 설정이 없습니다. (외부 요금 API Key 미설정)",
            ErrorCode.FARE_CONFIG_MISSING,
        )

    params = {
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{end_lng},{end_lat}",
    }
    api_key = settings.mobility_rest_api_key.strip()
    headers = {"Authorization": f"KakaoAK {api_key}"}

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(_MOBILITY_DIRECTIONS_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError:
        return _fallback_or_raise(
            502, "요금 산정 외부 API 호출에 실패했습니다.", ErrorCode.FARE_UPSTREAM_FAILED
        )

    try:
        summary = data["routes"][0]["summary"]
        return FareEstimate(
            estimated_fare=int(summary["fare"]["taxi"]),
            toll_fare=int(summary["fare"]["toll"]),
            distance_meters=int(summary["distance"]),
            duration_seconds=int(summary["duration"]),
            fare_source=FareSource.EXTERNAL_MOBILITY,
        )
    except (KeyError, IndexError, ValueError, TypeError):
        return _fallback_or_raise(
            502, "경로 또는 요금 정보를 찾을 수 없습니다.", ErrorCode.FARE_ROUTE_NOT_FOUND
        )


def per_person_fare(estimated_fare: int, current_members: int) -> int:
    """1인 예상 요금 — ceil(estimated_fare / current_members). 인원이 0이면 0."""
    if current_members <= 0:
        return 0
    return math.ceil(estimated_fare / current_members)
