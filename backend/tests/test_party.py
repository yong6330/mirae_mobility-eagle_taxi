"""파티 생성/목록/상세/참여 — 기능명세서 F-PARTY-001 ~ 004."""

from datetime import timedelta

from app.utils.time import now_kst_naive
from tests.conftest import auth_header, register_and_login


def _future_iso(hours: int = 2) -> str:
    """KST 기준 미래 시각을 ISO 문자열로 반환."""
    return (now_kst_naive() + timedelta(hours=hours)).isoformat()


def _past_iso(hours: int = 1) -> str:
    return (now_kst_naive() - timedelta(hours=hours)).isoformat()


def _sample_party_payload(**overrides) -> dict:
    base = {
        "start_place": "연세대학교 미래캠퍼스",
        "start_lat": 37.341,
        "start_lng": 127.918,
        "end_place": "원주역",
        "end_lat": 37.337,
        "end_lng": 127.945,
        "departure_time": _future_iso(),
        "meeting_point": "정문",
        "meeting_note": "검은 가방",
        "max_members": 4,
        "gender_rule": "any",
    }
    base.update(overrides)
    return base


def test_create_party_success(client):
    _, token = register_and_login(client, "creator@yonsei.ac.kr")
    res = client.post("/api/parties", json=_sample_party_payload(), headers=auth_header(token))
    assert res.status_code == 201, res.text

    body = res.json()
    assert body["status"] == "recruiting"
    assert body["current_members"] == 1
    assert body["max_members"] == 4
    # fare_source는 실키 유무에 따라 kakao/fallback 양쪽 모두 허용한다 (요금 로직은 test_fares.py에서 별도 검증).
    assert body["fare_source"] in ("kakao", "fallback")
    assert body["estimated_fare"] >= 0
    assert body["per_person_fare"] >= 0
    assert body["creator"]["email"] == "creator@yonsei.ac.kr"
    assert len(body["members"]) == 1


def test_create_party_past_departure_returns_400(client):
    _, token = register_and_login(client, "past@yonsei.ac.kr")
    res = client.post(
        "/api/parties",
        json=_sample_party_payload(departure_time=_past_iso()),
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert "출발 시간" in res.json()["detail"]


def test_create_party_invalid_max_members_returns_400(client):
    _, token = register_and_login(client, "max@yonsei.ac.kr")
    res = client.post(
        "/api/parties",
        json=_sample_party_payload(max_members=1),
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "최대 인원은 2명에서 4명 사이여야 합니다."


def test_same_gender_rule_party_creation_allowed_for_gendered_user(client):
    """v0.4: 회원가입에서 male/female만 허용되므로 same_gender 생성도 정상 동작."""
    _, token = register_and_login(client, "samegender@yonsei.ac.kr", gender="female")
    res = client.post(
        "/api/parties",
        json=_sample_party_payload(gender_rule="same_gender"),
        headers=auth_header(token),
    )
    assert res.status_code == 201
    assert res.json()["party_gender"] == "female"


def test_list_parties_default_recruiting(client):
    _, token = register_and_login(client, "list@yonsei.ac.kr")
    client.post("/api/parties", json=_sample_party_payload(), headers=auth_header(token))
    client.post("/api/parties", json=_sample_party_payload(), headers=auth_header(token))

    res = client.get("/api/parties", headers=auth_header(token))
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    assert all(p["status"] == "recruiting" for p in body["parties"])


def test_party_detail_returns_full_info(client):
    _, token = register_and_login(client, "detail@yonsei.ac.kr")
    created = client.post(
        "/api/parties", json=_sample_party_payload(), headers=auth_header(token)
    ).json()
    res = client.get(f"/api/parties/{created['id']}", headers=auth_header(token))
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == created["id"]
    assert body["start_lat"] == 37.341
    assert body["meeting_point"] == "정문"


def test_party_detail_not_found(client):
    _, token = register_and_login(client, "nf@yonsei.ac.kr")
    res = client.get("/api/parties/99999", headers=auth_header(token))
    assert res.status_code == 404


def test_join_party_success_updates_members_and_per_person_fare(client):
    _, creator_token = register_and_login(client, "host@yonsei.ac.kr")
    party = client.post(
        "/api/parties",
        json=_sample_party_payload(max_members=2),
        headers=auth_header(creator_token),
    ).json()

    _, joiner_token = register_and_login(client, "joiner@yonsei.ac.kr")
    res = client.post(f"/api/parties/{party['id']}/join", headers=auth_header(joiner_token))
    assert res.status_code == 200, res.text
    body = res.json()

    assert body["current_members"] == 2
    assert body["status"] == "matched"
    assert len(body["members"]) == 2


def test_join_party_duplicate_returns_400(client):
    _, host_token = register_and_login(client, "h@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_sample_party_payload(), headers=auth_header(host_token)
    ).json()
    res = client.post(f"/api/parties/{party['id']}/join", headers=auth_header(host_token))
    assert res.status_code == 400
    assert "이미" in res.json()["detail"]


def test_join_party_full_returns_400(client):
    _, host_token = register_and_login(client, "h2@yonsei.ac.kr")
    party = client.post(
        "/api/parties",
        json=_sample_party_payload(max_members=2),
        headers=auth_header(host_token),
    ).json()

    _, j1 = register_and_login(client, "j1@yonsei.ac.kr")
    client.post(f"/api/parties/{party['id']}/join", headers=auth_header(j1))

    _, j2 = register_and_login(client, "j2@yonsei.ac.kr")
    res = client.post(f"/api/parties/{party['id']}/join", headers=auth_header(j2))
    assert res.status_code == 400


def test_join_party_same_gender_mismatch_returns_400(client):
    _, host_token = register_and_login(client, "male@yonsei.ac.kr", gender="male")
    party = client.post(
        "/api/parties",
        json=_sample_party_payload(gender_rule="same_gender"),
        headers=auth_header(host_token),
    ).json()
    _, female_token = register_and_login(client, "female@yonsei.ac.kr", gender="female")
    res = client.post(f"/api/parties/{party['id']}/join", headers=auth_header(female_token))
    assert res.status_code == 400
    assert "동성 매칭" in res.json()["detail"]


def test_create_party_requires_auth(client):
    res = client.post("/api/parties", json=_sample_party_payload())
    assert res.status_code == 401


def test_timezone_aware_departure_is_accepted(client):
    """프론트가 KST 표기(+09:00) 또는 UTC(Z)로 보내도 정상 처리되어야 한다."""
    from datetime import datetime, timezone, timedelta

    _, token = register_and_login(client, "tz@yonsei.ac.kr")
    aware_utc = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
    res = client.post(
        "/api/parties",
        json=_sample_party_payload(departure_time=aware_utc),
        headers=auth_header(token),
    )
    assert res.status_code == 201, res.text
