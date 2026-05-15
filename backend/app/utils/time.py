"""시간대 처리 — 프로젝트의 모든 datetime을 KST naive로 통일한다.

명세서 4. 날짜·시간 기준:
  · 기본 시간 기준은 KST (Asia/Seoul)
  · API에서 사용하는 값은 ISO 8601 문자열
  · 프론트는 naive ISO 문자열(예: "2026-05-13T18:00:00")로 보내며, 이는 KST로 해석한다.

이 모듈의 규칙:
  · `now_kst_naive()`로 현재 시각을 가져온다 (KST 기준 naive)
  · 외부에서 들어오는 datetime은 `to_kst_naive()`로 정규화한다
    - naive datetime은 이미 KST로 가정한다 (명세서 기준)
    - timezone-aware datetime은 KST로 변환 후 tz 제거한다
"""

from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))


def now_kst_naive() -> datetime:
    """현재 시각을 KST 기준 naive datetime으로 반환한다."""
    return datetime.now(KST).replace(tzinfo=None)


def to_kst_naive(dt: datetime) -> datetime:
    """어떤 datetime이든 KST naive로 변환한다.

    · naive 입력 → 이미 KST로 간주하고 그대로 반환
    · timezone-aware 입력 → KST로 변환 후 tzinfo 제거

    주의: naive UTC를 넘기면 9시간 어긋난다. 자세한 내용은 NOTES.md 1번 항목 참고.
    내부 코드에서 현재 시각이 필요하면 datetime.now()/utcnow() 금지, now_kst_naive() 사용.
    """
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(KST).replace(tzinfo=None)
