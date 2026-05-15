"""요금 산정 서비스 — 기능명세서 F-PARTY-005.

Kakao Mobility Directions API를 호출해 estimated_fare/toll_fare/distance/duration을 가져온다.
API Key가 없거나 호출이 실패하면 모든 값을 0으로 채운 fallback 결과를 반환한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import httpx

from app.config import settings
from app.constants import FareSource

_KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"


@dataclass
class FareEstimate:
    """요금 산정 결과 — DB 컬럼과 1:1 매칭된다."""

    estimated_fare: int
    toll_fare: int
    distance_meters: int
    duration_seconds: int
    fare_source: str

    @classmethod
    def fallback(cls) -> "FareEstimate":
        """Kakao 호출 불가/실패 시 0으로 채운 결과."""
        return cls(
            estimated_fare=0,
            toll_fare=0,
            distance_meters=0,
            duration_seconds=0,
            fare_source=FareSource.FALLBACK,
        )


def estimate_fare(
    start_lat: float, start_lng: float, end_lat: float, end_lng: float
) -> FareEstimate:
    """Kakao Mobility Directions API로 요금/거리/소요시간을 조회한다.

    Key가 없거나 호출이 실패하면 자동으로 fallback 결과를 반환한다 (예외 던지지 않음).
    """
    if not settings.kakao_rest_api_key:
        return FareEstimate.fallback()

    params = {
        "origin": f"{start_lng},{start_lat}",
        "destination": f"{end_lng},{end_lat}",
    }
    headers = {"Authorization": f"KakaoAK {settings.kakao_rest_api_key}"}

    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(_KAKAO_DIRECTIONS_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        summary = data["routes"][0]["summary"]
        return FareEstimate(
            estimated_fare=int(summary["fare"]["taxi"]),
            toll_fare=int(summary["fare"]["toll"]),
            distance_meters=int(summary["distance"]),
            duration_seconds=int(summary["duration"]),
            fare_source=FareSource.KAKAO,
        )
    except (httpx.HTTPError, KeyError, IndexError, ValueError):
        # 네트워크/응답 형식 오류 — MVP에서는 0원 fallback으로 처리하고 파티 생성 자체는 계속 진행한다.
        return FareEstimate.fallback()


def per_person_fare(estimated_fare: int, current_members: int) -> int:
    """1인 예상 요금 — ceil(estimated_fare / current_members). 인원이 0이면 0."""
    if current_members <= 0:
        return 0
    return math.ceil(estimated_fare / current_members)
