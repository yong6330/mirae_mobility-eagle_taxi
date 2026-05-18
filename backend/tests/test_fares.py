"""GET /api/fares/estimate — 기능명세서 F-PARTY-005, FARE-001."""

from tests.conftest import auth_header, register_and_login


def test_fare_estimate_requires_auth(client):
    """비로그인이면 401."""
    res = client.get("/api/fares/estimate", params={
        "start_lat": 37.341, "start_lng": 127.918,
        "end_lat": 37.337, "end_lng": 127.945,
    })
    assert res.status_code == 401


def test_fare_estimate_returns_fallback_when_no_kakao_key(client):
    """Kakao Key가 없으면 모든 값 0 + fare_source=fallback."""
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
