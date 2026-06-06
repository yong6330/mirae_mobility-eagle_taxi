"""GET /api/my/parties — 기능명세서 F-PARTY-012."""

from datetime import timedelta

from app.utils.time import now_kst_naive
from tests.conftest import auth_header, register_and_login


def _future_iso(hours: int = 2) -> str:
    return (now_kst_naive() + timedelta(hours=hours)).isoformat()


def _party_payload(**overrides) -> dict:
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


def test_my_parties_requires_auth(client):
    res = client.get("/api/my/parties")
    assert res.status_code == 401


def test_my_parties_empty(client):
    """파티가 없으면 created_parties / joined_parties 모두 빈 배열."""
    _, token = register_and_login(client, "empty@yonsei.ac.kr")
    res = client.get("/api/my/parties", headers=auth_header(token))
    assert res.status_code == 200
    body = res.json()
    assert body == {"created_parties": [], "joined_parties": []}


def test_my_parties_only_created(client):
    """내가 만든 파티는 created_parties에만 표시되고 joined_parties에는 중복되지 않는다."""
    _, token = register_and_login(client, "creator@yonsei.ac.kr")
    p1 = client.post("/api/parties", json=_party_payload(), headers=auth_header(token)).json()
    p2 = client.post("/api/parties", json=_party_payload(), headers=auth_header(token)).json()

    res = client.get("/api/my/parties", headers=auth_header(token))
    assert res.status_code == 200
    body = res.json()
    created_ids = {p["id"] for p in body["created_parties"]}
    assert created_ids == {p1["id"], p2["id"]}
    assert body["joined_parties"] == []  # 생성자는 joined에 중복 표시 X


def test_my_parties_only_joined(client):
    """다른 사람 파티에 참여하면 joined_parties에만 표시된다."""
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    host_party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    _, joiner_token = register_and_login(client, "joiner@yonsei.ac.kr")
    client.post(f"/api/parties/{host_party['id']}/join", headers=auth_header(joiner_token))

    res = client.get("/api/my/parties", headers=auth_header(joiner_token))
    assert res.status_code == 200
    body = res.json()
    assert body["created_parties"] == []
    joined_ids = {p["id"] for p in body["joined_parties"]}
    assert joined_ids == {host_party["id"]}


def test_my_parties_mixed(client):
    """내가 만든 것과 참여한 것이 섞여 있을 때 정확히 구분된다.

    v0.4 시간 충돌 검증을 피하려고 alice의 파티와 bob의 파티 출발시간을 충분히 떨어뜨린다.
    """
    _, alice_token = register_and_login(client, "alice@yonsei.ac.kr")
    alice_party = client.post(
        "/api/parties",
        json=_party_payload(departure_time=_future_iso(hours=2)),
        headers=auth_header(alice_token),
    ).json()

    _, bob_token = register_and_login(client, "bob@yonsei.ac.kr")
    bob_party = client.post(
        "/api/parties",
        json=_party_payload(departure_time=_future_iso(hours=10)),  # 8시간 차이
        headers=auth_header(bob_token),
    ).json()

    # alice가 bob의 파티에 참여 (시간 충돌 안 남)
    join_res = client.post(f"/api/parties/{bob_party['id']}/join", headers=auth_header(alice_token))
    assert join_res.status_code == 200, join_res.text

    res = client.get("/api/my/parties", headers=auth_header(alice_token))
    assert res.status_code == 200
    body = res.json()
    assert {p["id"] for p in body["created_parties"]} == {alice_party["id"]}
    assert {p["id"] for p in body["joined_parties"]} == {bob_party["id"]}


def test_my_parties_latest_first(client):
    """created_parties는 최신순(created_at desc) 정렬."""
    _, token = register_and_login(client, "order@yonsei.ac.kr")
    p1 = client.post("/api/parties", json=_party_payload(), headers=auth_header(token)).json()
    p2 = client.post("/api/parties", json=_party_payload(), headers=auth_header(token)).json()
    p3 = client.post("/api/parties", json=_party_payload(), headers=auth_header(token)).json()

    res = client.get("/api/my/parties", headers=auth_header(token))
    body = res.json()
    ids_in_order = [p["id"] for p in body["created_parties"]]
    assert ids_in_order == [p3["id"], p2["id"], p1["id"]]
