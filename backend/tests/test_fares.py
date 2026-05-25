"""GET /api/fares/estimate — 기능명세서 F-PARTY-005, FARE-001.

테스트 정책 — 실키 의존 분리:
  · 로컬 `.env`에 Kakao Key가 있어도 fallback 동작은 monkeypatch로 키를 비워 검증한다.
  · 실키 경로는 별도 통합 테스트(network 필요)로 분리할 수 있도록 fare_source만 'kakao'/'fallback' 둘 중 하나임을 확인한다.
"""

from app.services import fare as fare_service
from tests.conftest import auth_header, register_and_login


def test_fare_estimate_requires_auth(client):
    """비로그인이면 401."""
    res = client.get("/api/fares/estimate", params={
        "start_lat": 37.341, "start_lng": 127.918,
        "end_lat": 37.337, "end_lng": 127.945,
    })
    assert res.status_code == 401


def test_fare_estimate_returns_fallback_when_no_kakao_key(client, monkeypatch):
    """Kakao Key가 없으면 모든 값 0 + fare_source=fallback.

    실키가 .env에 있어도 이 테스트는 키를 비워 fallback 경로만 검증한다.
    """
    monkeypatch.setattr(fare_service.settings, "kakao_rest_api_key", "")

    _, token = register_and_login(client, "fare@yonsei.ac.kr")
    res = client.get(
        "/api/fares/estimate",
        params={
            "start_lat": 37.341, "start_lng": 127.918,
            "end_lat": 37.337, "end_lng": 127.945,
        },
        headers=auth_header(token),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["estimated_fare"] == 0
    assert body["toll_fare"] == 0
    assert body["distance_meters"] == 0
    assert body["duration_seconds"] == 0
    assert body["fare_source"] == "fallback"


def test_fare_estimate_missing_query_returns_400(client):
    """좌표 누락 시 400 + 한글 메시지."""
    _, token = register_and_login(client, "missing@yonsei.ac.kr")
    res = client.get(
        "/api/fares/estimate",
        params={"start_lat": 37.341, "start_lng": 127.918},  # end 누락
        headers=auth_header(token),
    )
    assert res.status_code == 400
