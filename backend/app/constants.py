"""프로젝트 전역 상수.

기능명세서에 등장하는 값(상태/성별/권한/매칭 옵션 등)을 한 곳에 모았다.
새 상태 값을 추가하거나 표기를 바꾸려면 이 파일만 수정하면 된다.
"""

from typing import Literal


class Gender:
    """사용자 성별 — 기능명세서 / API 명세서 8-1."""

    MALE = "male"
    FEMALE = "female"
    NONE = "none"

    ALL: tuple[str, ...] = (MALE, FEMALE, NONE)


GenderType = Literal["male", "female", "none"]


class UserRole:
    """사용자 권한 — API 명세서 8-2."""

    USER = "user"
    ADMIN = "admin"

    ALL: tuple[str, ...] = (USER, ADMIN)


UserRoleType = Literal["user", "admin"]


class PartyStatus:
    """파티 상태 — 기능명세서 F-PARTY-006 v0.4 / API 명세서 8-3."""

    RECRUITING = "recruiting"  # 모집 중
    MATCHED = "matched"  # 매칭 완료 (최대 인원 도달)
    CANCELED = "canceled"  # 생성자가 취소
    EXPIRED = "expired"  # 출발 시간 만료 (recruiting 상태에서 시간 지남)
    COMPLETED = "completed"  # 이용 완료 (matched 상태에서 출발 시간 지남)

    ALL: tuple[str, ...] = (RECRUITING, MATCHED, CANCELED, EXPIRED, COMPLETED)


PartyStatusType = Literal["recruiting", "matched", "canceled", "expired", "completed"]


class GenderRule:
    """파티 성별 매칭 옵션 — 기능명세서 F-PARTY-013."""

    ANY = "any"  # 누구나 참여 가능
    SAME_GENDER = "same_gender"  # 생성자와 같은 성별만 참여 가능

    ALL: tuple[str, ...] = (ANY, SAME_GENDER)


GenderRuleType = Literal["any", "same_gender"]


class FareSource:
    """요금 출처 — 기능명세서 F-PARTY-005 출력값 fare_source."""

    KAKAO = "kakao"  # Kakao Mobility Directions API 응답 기반
    FALLBACK = "fallback"  # API Key 없거나 호출 실패 시 0원 처리

    ALL: tuple[str, ...] = (KAKAO, FALLBACK)


FareSourceType = Literal["kakao", "fallback"]
