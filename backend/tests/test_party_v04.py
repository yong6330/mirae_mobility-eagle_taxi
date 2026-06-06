"""명세서 v0.4 신규/변경 기능 테스트.

F-PARTY-004 시간 충돌, F-PARTY-007 검색, F-PARTY-008 추천,
F-PARTY-010 참여 취소, F-PARTY-011 파티 취소.
"""

from datetime import timedelta

from app.utils.time import now_kst_naive
from tests.conftest import auth_header, register_and_login


def _iso(dt) -> str:
    return dt.isoformat()


def _payload(departure, **overrides) -> dict:
    base = {
        "start_place": "연세대학교 미래캠퍼스",
        "start_lat": 37.341,
        "start_lng": 127.918,
        "end_place": "원주역",
        "end_lat": 37.337,
        "end_lng": 127.945,
        "departure_time": _iso(departure),
        "meeting_point": "정문",
        "meeting_note": "검은 가방",
        "max_members": 4,
        "gender_rule": "any",
    }
    base.update(overrides)
    return base


# ────────────────────────────────────────────────────────────────────
# F-PARTY-004: 같은 시간대 중복 참여 차단 (v0.4 신규)
# ────────────────────────────────────────────────────────────────────

def test_join_party_blocked_when_time_conflicts_with_another_party(client):
    """같은 시간대(±60분)에 이미 다른 파티에 참여 중이면 join 거부."""
    base_time = now_kst_naive() + timedelta(hours=3)

    _, host1_token = register_and_login(client, "h1@yonsei.ac.kr")
    party1 = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host1_token)
    ).json()

    _, host2_token = register_and_login(client, "h2@yonsei.ac.kr")
    # base_time + 10분 → ±60분 윈도우 내
    party2 = client.post(
        "/api/parties",
        json=_payload(base_time + timedelta(minutes=10)),
        headers=auth_header(host2_token),
    ).json()

    _, user_token = register_and_login(client, "user@yonsei.ac.kr")
    # 첫 파티 참여 OK
    r1 = client.post(f"/api/parties/{party1['id']}/join", headers=auth_header(user_token))
    assert r1.status_code == 200

    # 같은 시간대 두 번째 파티 참여 → 차단 (명세 PARTY-006: 409 PARTY_TIME_OVERLAP)
    r2 = client.post(f"/api/parties/{party2['id']}/join", headers=auth_header(user_token))
    assert r2.status_code == 409
    assert "같은 시간대" in r2.json()["detail"]
    assert r2.json()["error_code"] == "PARTY_TIME_OVERLAP"


def test_join_party_allowed_when_time_far_apart(client):
    """시간대가 충분히 떨어져 있으면(±60분 밖) 두 파티 모두 참여 OK."""
    base_time = now_kst_naive() + timedelta(hours=3)

    _, host1_token = register_and_login(client, "h1@yonsei.ac.kr")
    party1 = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host1_token)
    ).json()

    _, host2_token = register_and_login(client, "h2@yonsei.ac.kr")
    party2 = client.post(
        "/api/parties",
        json=_payload(base_time + timedelta(hours=5)),
        headers=auth_header(host2_token),
    ).json()

    _, user_token = register_and_login(client, "user@yonsei.ac.kr")
    assert client.post(f"/api/parties/{party1['id']}/join", headers=auth_header(user_token)).status_code == 200
    assert client.post(f"/api/parties/{party2['id']}/join", headers=auth_header(user_token)).status_code == 200


# ────────────────────────────────────────────────────────────────────
# F-PARTY-007: 파티 검색
# ────────────────────────────────────────────────────────────────────

def test_search_parties_by_start_place(client):
    _, token = register_and_login(client, "search@yonsei.ac.kr")
    base = now_kst_naive() + timedelta(hours=2)
    client.post("/api/parties", json=_payload(base, start_place="연세대 정문"), headers=auth_header(token))
    client.post(
        "/api/parties",
        json=_payload(base + timedelta(hours=3), start_place="원주 시외버스터미널"),
        headers=auth_header(token),
    )

    res = client.get(
        "/api/parties/search", params={"start_place": "연세"}, headers=auth_header(token)
    )
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert "연세" in body["parties"][0]["start_place"]


def test_search_parties_no_match_returns_empty(client):
    _, token = register_and_login(client, "search2@yonsei.ac.kr")
    res = client.get(
        "/api/parties/search", params={"start_place": "없는장소"}, headers=auth_header(token)
    )
    assert res.status_code == 200
    assert res.json()["total"] == 0


# ────────────────────────────────────────────────────────────────────
# F-PARTY-008: 유사 파티 추천 (35/35/30/20/10 점수표)
# ────────────────────────────────────────────────────────────────────

def test_recommend_returns_score_sorted(client):
    _, token = register_and_login(client, "rec@yonsei.ac.kr")
    target_time = now_kst_naive() + timedelta(hours=4)

    # 완전 일치 (출발지+도착지+10분 이내) → 35+35+30 = 100점
    p_perfect = client.post(
        "/api/parties",
        json=_payload(
            target_time + timedelta(minutes=5),
            start_place="연세대 정문",
            end_place="원주역",
        ),
        headers=auth_header(token),
    ).json()

    # 출발지만 일치, 시간 25분 차이 → 25분은 20분 초과·30분 이내 → 35 + 10 = 45점
    p_partial = client.post(
        "/api/parties",
        json=_payload(
            target_time + timedelta(minutes=25),
            start_place="연세대 정문",
            end_place="다른 도착지",
        ),
        headers=auth_header(token),
    ).json()

    res = client.get(
        "/api/parties/recommend",
        params={
            "start_place": "연세대 정문",
            "end_place": "원주역",
            "departure_time": _iso(target_time),
            "time_range_minutes": 30,
        },
        headers=auth_header(token),
    )
    assert res.status_code == 200
    parties = res.json()["parties"]
    assert len(parties) == 2
    assert parties[0]["id"] == p_perfect["id"]
    assert parties[0]["match_score"] == 100
    assert parties[1]["id"] == p_partial["id"]
    assert parties[1]["match_score"] == 45


def test_recommend_excludes_full_or_canceled(client):
    """matched/canceled/expired 파티는 추천 대상 X."""
    _, host_token = register_and_login(client, "rh@yonsei.ac.kr")
    target_time = now_kst_naive() + timedelta(hours=4)
    party = client.post(
        "/api/parties",
        json=_payload(target_time, max_members=2),
        headers=auth_header(host_token),
    ).json()

    # joiner가 들어와서 matched
    _, joiner_token = register_and_login(client, "rj@yonsei.ac.kr")
    client.post(f"/api/parties/{party['id']}/join", headers=auth_header(joiner_token))

    _, search_token = register_and_login(client, "rs@yonsei.ac.kr")
    res = client.get(
        "/api/parties/recommend",
        params={
            "start_place": "연세대학교 미래캠퍼스",
            "end_place": "원주역",
            "departure_time": _iso(target_time),
        },
        headers=auth_header(search_token),
    )
    assert res.status_code == 200
    assert res.json()["parties"] == []


# ────────────────────────────────────────────────────────────────────
# F-PARTY-010: 참여 취소
# ────────────────────────────────────────────────────────────────────

def test_leave_party_success(client):
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "lh@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_payload(base_time, max_members=2), headers=auth_header(host_token)
    ).json()
    _, joiner_token = register_and_login(client, "lj@yonsei.ac.kr")
    client.post(f"/api/parties/{party['id']}/join", headers=auth_header(joiner_token))

    res = client.delete(f"/api/parties/{party['id']}/leave", headers=auth_header(joiner_token))
    assert res.status_code == 200
    body = res.json()
    assert body["current_members"] == 1
    assert body["status"] == "recruiting"  # matched에서 다시 recruiting으로


def test_leave_party_creator_blocked(client):
    """생성자는 leave 불가."""
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "lh2@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host_token)
    ).json()

    res = client.delete(f"/api/parties/{party['id']}/leave", headers=auth_header(host_token))
    assert res.status_code == 409  # 명세 PARTY-007: 생성자 이탈은 409
    assert "생성자" in res.json()["detail"]
    assert res.json()["error_code"] == "PARTY_CREATOR_CANNOT_LEAVE"


def test_leave_party_not_a_member(client):
    """참여하지 않은 파티는 leave 거부."""
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "lh3@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host_token)
    ).json()
    _, other_token = register_and_login(client, "lo@yonsei.ac.kr")

    res = client.delete(f"/api/parties/{party['id']}/leave", headers=auth_header(other_token))
    assert res.status_code == 409  # 명세 PARTY-007: 미참여자 취소는 409
    assert "참여하지 않은" in res.json()["detail"]
    assert res.json()["error_code"] == "PARTY_NOT_JOINED"


# ────────────────────────────────────────────────────────────────────
# F-PARTY-011: 파티 취소 (생성자)
# ────────────────────────────────────────────────────────────────────

def test_cancel_party_by_creator(client):
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "ch@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host_token)
    ).json()

    res = client.patch(
        f"/api/parties/{party['id']}/cancel",
        json={"cancel_reason": "출발 시간 못 맞춤"},
        headers=auth_header(host_token),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "canceled"
    assert body["cancel_reason"] == "출발 시간 못 맞춤"
    assert body["canceled_at"] is not None


def test_cancel_party_blocked_for_non_creator(client):
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "ch2@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host_token)
    ).json()
    _, other_token = register_and_login(client, "co@yonsei.ac.kr")

    res = client.patch(
        f"/api/parties/{party['id']}/cancel",
        json={"cancel_reason": "장난"},
        headers=auth_header(other_token),
    )
    assert res.status_code == 403


def test_canceled_party_cannot_be_joined(client):
    base_time = now_kst_naive() + timedelta(hours=3)
    _, host_token = register_and_login(client, "ch3@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_payload(base_time), headers=auth_header(host_token)
    ).json()
    client.patch(
        f"/api/parties/{party['id']}/cancel",
        json={"cancel_reason": "취소"},
        headers=auth_header(host_token),
    )

    _, other_token = register_and_login(client, "cj@yonsei.ac.kr")
    res = client.post(f"/api/parties/{party['id']}/join", headers=auth_header(other_token))
    assert res.status_code == 409  # 명세 PARTY-006: 취소된 파티 참여는 409
    assert "취소된 파티" in res.json()["detail"]
    assert res.json()["error_code"] == "PARTY_NOT_RECRUITING"
