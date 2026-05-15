"""서버 상태 확인 라우터 — 기능명세서 F-SYS-001."""

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/api/health")
def health():
    """서버가 정상 동작 중인지 확인한다."""
    return {"status": "ok", "service": "eagle-taxi-api"}
