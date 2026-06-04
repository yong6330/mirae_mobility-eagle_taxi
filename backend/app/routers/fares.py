"""요금 미리보기 라우터 — 기능명세서 F-PARTY-005, API 명세서 FARE-001.

파티 생성 화면에서 사용자가 출발지·도착지를 선택한 직후, 실제로 파티를 만들기 전에
예상 택시비를 한 번 확인할 수 있도록 하는 단독 미리보기 API.
파티 생성 시에는 POST /api/parties 내부에서 동일한 산정 로직이 다시 호출된다.
"""

from fastapi import APIRouter, Depends, Query

from app.deps import get_current_user
from app.models import User
from app.schemas.party import FareEstimateOut
from app.services.fare import estimate_fare

router = APIRouter(prefix="/api/fares", tags=["fares"])


@router.get("/estimate", response_model=FareEstimateOut)
def get_fare_estimate(
    start_lat: float = Query(..., description="출발지 위도"),
    start_lng: float = Query(..., description="출발지 경도"),
    end_lat: float = Query(..., description="도착지 위도"),
    end_lng: float = Query(..., description="도착지 경도"),
    current_user: User = Depends(get_current_user),
):
    """좌표 기반 예상 요금 미리보기.

    Kakao Mobility Directions API 호출 결과를 그대로 반환한다.
    Key가 없거나 호출 실패 시 fallback(모든 값 0, fare_source="fallback")으로 응답한다.
    """
    result = estimate_fare(start_lat, start_lng, end_lat, end_lng)
    return FareEstimateOut(
        estimated_fare=result.estimated_fare,
        toll_fare=result.toll_fare,
        distance_meters=result.distance_meters,
        duration_seconds=result.duration_seconds,
        fare_source=result.fare_source,
        fare_warning=result.fare_warning,
    )
