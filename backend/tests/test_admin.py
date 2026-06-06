"""관리자 API 테스트 — 명세서 v0.4 ADMIN-001 ~ 010 / F-ADMIN-001 ~ 010.

테스트 전략
  - admin 계정은 conftest의 register_and_login 후 DB를 직접 조작해 role='admin'으로 승격.
    (회원가입 API는 role을 입력받지 않으므로 정상 경로다.)
  - 모든 ADMIN 엔드포인트는 401(미로그인) / 403(일반 사용자) 공통으로 검증.
"""

from datetime import timedelta

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User
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


def _make_admin(email: str = "admin@yonsei.ac.kr") -> tuple[dict, str]:
    """admin 계정 생성 — register 후 DB에서 role=admin으로 승격."""
    from fastapi.testclient import TestClient

    from app.main import app

    c = TestClient(app)
    user, token = register_and_login(c, email, name="관리자")
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.role = "admin"
        db.commit()
    # 토큰은 role이 바뀌어도 유효 (sub=user_id만 본다)
    return user, token


# ──────────────────────────────────────────────────────────────
# 공통: 인증/권한
# ──────────────────────────────────────────────────────────────


def test_admin_requires_auth(client):
    res = client.get("/api/admin/stats")
    assert res.status_code == 401


def test_admin_rejects_normal_user(client):
    _, token = register_and_login(client, "user@yonsei.ac.kr")
    res = client.get("/api/admin/stats", headers=auth_header(token))
    assert res.status_code == 403
    assert "관리자" in res.json()["detail"]


def test_admin_rejects_inactive_admin(client):
    """비활성 사용자는 admin이라도 거부."""
    _, token = _make_admin()
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.email == "admin@yonsei.ac.kr")).scalar_one()
        u.is_active = False
        db.commit()
    res = client.get("/api/admin/stats", headers=auth_header(token))
    assert res.status_code == 403
    assert "비활성" in res.json()["detail"]


# ──────────────────────────────────────────────────────────────
# ADMIN-001: GET /api/admin/stats
# ──────────────────────────────────────────────────────────────


def test_stats_empty_state(client):
    _, admin_token = _make_admin()
    res = client.get("/api/admin/stats", headers=auth_header(admin_token))
    assert res.status_code == 200
    body = res.json()
    assert body["total_users"] == 1  # admin 본인
    assert body["active_users"] == 1
    assert body["total_parties"] == 0
    assert body["total_messages"] == 0
    assert body["recruiting_parties"] == 0


def test_stats_counts_after_activity(client):
    _, admin_token = _make_admin()
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    client.post("/api/parties", json=_party_payload(), headers=auth_header(host_token))

    res = client.get("/api/admin/stats", headers=auth_header(admin_token))
    body = res.json()
    assert body["total_users"] == 2
    assert body["total_parties"] == 1
    assert body["recruiting_parties"] == 1


# ──────────────────────────────────────────────────────────────
# ADMIN-002: GET /api/admin/parties/recent
# ──────────────────────────────────────────────────────────────


def test_recent_parties_empty(client):
    _, token = _make_admin()
    res = client.get("/api/admin/parties/recent", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json() == {"items": []}


def test_recent_parties_returns_latest_first(client):
    _, admin_token = _make_admin()
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    p1 = client.post(
        "/api/parties",
        json={**_party_payload(), "start_place": "A지점"},
        headers=auth_header(host_token),
    ).json()
    p2 = client.post(
        "/api/parties",
        json={**_party_payload(), "start_place": "B지점", "departure_time": _future_iso(5)},
        headers=auth_header(host_token),
    ).json()

    res = client.get(
        "/api/admin/parties/recent?limit=5", headers=auth_header(admin_token)
    )
    items = res.json()["items"]
    assert len(items) == 2
    assert items[0]["id"] == p2["id"]  # 최신
    assert items[1]["id"] == p1["id"]
    assert items[0]["creator_name"] == "테스터"


# ──────────────────────────────────────────────────────────────
# ADMIN-003: GET /api/admin/users
# ──────────────────────────────────────────────────────────────


def test_users_list_excludes_password_hash(client):
    _, token = _make_admin()
    register_and_login(client, "x@yonsei.ac.kr")
    res = client.get("/api/admin/users", headers=auth_header(token))
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 2
    for item in body["items"]:
        assert "password_hash" not in item
        assert "password" not in item


def test_users_list_pagination(client):
    _, token = _make_admin()
    for i in range(5):
        register_and_login(client, f"u{i}@yonsei.ac.kr")
    res = client.get("/api/admin/users?page=1&limit=3", headers=auth_header(token))
    body = res.json()
    assert body["total"] == 6  # admin + 5
    assert len(body["items"]) == 3
    assert body["page"] == 1
    assert body["limit"] == 3


# ──────────────────────────────────────────────────────────────
# ADMIN-004: GET /api/admin/parties (with filter)
# ──────────────────────────────────────────────────────────────


def test_parties_filter_by_status(client):
    _, admin_token = _make_admin()
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    client.post("/api/parties", json=_party_payload(), headers=auth_header(host_token))

    res = client.get(
        "/api/admin/parties?status=recruiting", headers=auth_header(admin_token)
    )
    body = res.json()
    assert body["total"] == 1
    res2 = client.get(
        "/api/admin/parties?status=canceled", headers=auth_header(admin_token)
    )
    assert res2.json()["total"] == 0


def test_parties_filter_by_keyword(client):
    _, admin_token = _make_admin()
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    client.post(
        "/api/parties",
        json={**_party_payload(), "start_place": "특이지점XYZ"},
        headers=auth_header(host_token),
    )
    client.post(
        "/api/parties",
        json={**_party_payload(), "departure_time": _future_iso(5)},
        headers=auth_header(host_token),
    )

    res = client.get(
        "/api/admin/parties?keyword=XYZ", headers=auth_header(admin_token)
    )
    assert res.json()["total"] == 1


def test_parties_invalid_status_returns_400(client):
    _, token = _make_admin()
    res = client.get(
        "/api/admin/parties?status=invalid", headers=auth_header(token)
    )
    assert res.status_code == 400


# ──────────────────────────────────────────────────────────────
# ADMIN-005: PATCH /api/admin/parties/{id}/status
# ──────────────────────────────────────────────────────────────


def test_update_party_status_to_canceled(client):
    _, admin_token = _make_admin()
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    res = client.patch(
        f"/api/admin/parties/{party['id']}/status",
        json={"status": "canceled", "admin_note": "관리자 확인 후 취소"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["status"] == "canceled"


def test_update_party_status_not_found(client):
    _, token = _make_admin()
    res = client.patch(
        "/api/admin/parties/99999/status",
        json={"status": "canceled"},
        headers=auth_header(token),
    )
    assert res.status_code == 404


def test_update_party_status_invalid_value(client):
    _, admin_token = _make_admin()
    _, host_token = register_and_login(client, "host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()
    res = client.patch(
        f"/api/admin/parties/{party['id']}/status",
        json={"status": "weird_status"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 400


# ──────────────────────────────────────────────────────────────
# ADMIN-006: PATCH /api/admin/users/{id}/role
# ──────────────────────────────────────────────────────────────


def test_update_user_role_promote_to_admin(client):
    _, admin_token = _make_admin()
    user, _ = register_and_login(client, "target@yonsei.ac.kr")

    res = client.patch(
        f"/api/admin/users/{user['id']}/role",
        json={"role": "admin"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_update_user_role_invalid(client):
    _, admin_token = _make_admin()
    user, _ = register_and_login(client, "target@yonsei.ac.kr")
    res = client.patch(
        f"/api/admin/users/{user['id']}/role",
        json={"role": "superadmin"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 400


def test_update_user_role_not_found(client):
    _, admin_token = _make_admin()
    res = client.patch(
        "/api/admin/users/99999/role",
        json={"role": "admin"},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────
# ADMIN-007: PATCH /api/admin/users/{id}/status
# ──────────────────────────────────────────────────────────────


def test_update_user_active_deactivate(client):
    _, admin_token = _make_admin()
    user, target_token = register_and_login(client, "target@yonsei.ac.kr")

    res = client.patch(
        f"/api/admin/users/{user['id']}/status",
        json={"is_active": False},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 200
    assert res.json()["is_active"] is False

    # 비활성 사용자는 me 조회에서 차단되거나 즉시 영향이 있어야 함 (auth.py에 따라).
    # 최소한 admin 응답에서 is_active=False가 정상 반영되는지 확인.


def test_update_user_active_not_found(client):
    _, admin_token = _make_admin()
    res = client.patch(
        "/api/admin/users/99999/status",
        json={"is_active": False},
        headers=auth_header(admin_token),
    )
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────
# ADMIN-008: GET /api/admin/messages/recent
# ──────────────────────────────────────────────────────────────


def test_recent_messages_empty(client):
    _, token = _make_admin()
    res = client.get("/api/admin/messages/recent", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json() == {"recent_messages": []}


def test_recent_messages_returns_messages(client):
    """WebSocket 거치지 않고 DB에 직접 메시지 삽입 후 조회."""
    from app.models import Message, Party, PartyMember

    _, admin_token = _make_admin()
    user, host_token = register_and_login(client, "host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    with SessionLocal() as db:
        db.add(Message(party_id=party["id"], user_id=user["id"], content="첫 메시지"))
        db.add(Message(party_id=party["id"], user_id=user["id"], content="둘째 메시지"))
        db.commit()

    res = client.get(
        "/api/admin/messages/recent?limit=10", headers=auth_header(admin_token)
    )
    items = res.json()["recent_messages"]
    assert len(items) == 2
    assert items[0]["user_name"] == "테스터"
    # 최신순
    assert items[0]["content"] == "둘째 메시지"


# ──────────────────────────────────────────────────────────────
# ADMIN-009: GET /api/admin/users/{id}
# ──────────────────────────────────────────────────────────────


def test_user_detail_with_counts(client):
    from app.models import Message

    _, admin_token = _make_admin()
    user, host_token = register_and_login(client, "host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    with SessionLocal() as db:
        db.add(Message(party_id=party["id"], user_id=user["id"], content="A"))
        db.add(Message(party_id=party["id"], user_id=user["id"], content="B"))
        db.commit()

    res = client.get(
        f"/api/admin/users/{user['id']}", headers=auth_header(admin_token)
    )
    assert res.status_code == 200
    body = res.json()
    assert body["user"]["id"] == user["id"]
    assert "password_hash" not in body["user"]
    assert body["created_parties_count"] == 1
    assert body["joined_parties_count"] == 1  # 생성자는 자동 참여
    assert body["message_count"] == 2


def test_user_detail_not_found(client):
    _, token = _make_admin()
    res = client.get("/api/admin/users/99999", headers=auth_header(token))
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────
# ADMIN-010: GET /api/admin/parties/{id}
# ──────────────────────────────────────────────────────────────


def test_party_detail_with_members_and_message_count(client):
    from app.models import Message

    _, admin_token = _make_admin()
    user, host_token = register_and_login(client, "host@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()
    with SessionLocal() as db:
        db.add(Message(party_id=party["id"], user_id=user["id"], content="A"))
        db.commit()

    res = client.get(
        f"/api/admin/parties/{party['id']}", headers=auth_header(admin_token)
    )
    body = res.json()
    assert body["party"]["id"] == party["id"]
    assert body["party"]["current_members"] == 1
    assert len(body["members"]) == 1
    assert body["members"][0]["name"] == "테스터"
    assert body["messages_count"] == 1


def test_party_detail_not_found(client):
    _, token = _make_admin()
    res = client.get("/api/admin/parties/99999", headers=auth_header(token))
    assert res.status_code == 404


# ──────────────────────────────────────────────────────────────
# ADMIN-011: GET /api/admin/system/status
# ──────────────────────────────────────────────────────────────


def test_system_status_returns_fields(client):
    _, admin_token = _make_admin()
    res = client.get("/api/admin/system/status", headers=auth_header(admin_token))
    assert res.status_code == 200
    body = res.json()
    assert body["api_status"] == "ok"
    assert body["db_status"] == "ok"
    assert isinstance(body["mobility_provider_configured"], bool)
    assert isinstance(body["fare_fallback_enabled"], bool)
    assert "server_time" in body


def test_system_status_requires_admin(client):
    _, token = register_and_login(client, "normal@yonsei.ac.kr")
    assert client.get("/api/admin/system/status").status_code == 401
    assert client.get(
        "/api/admin/system/status", headers=auth_header(token)
    ).status_code == 403


# ──────────────────────────────────────────────────────────────
# ADMIN-012: GET /api/admin/actions (조작 기록)
# ──────────────────────────────────────────────────────────────


def test_admin_actions_logged_on_role_and_status_changes(client):
    """ADMIN-006/007/005 수행 시 admin_actions에 기록되고 ADMIN-012로 조회된다."""
    _, admin_token = _make_admin()
    target, host_token = register_and_login(client, "target@yonsei.ac.kr")
    party = client.post(
        "/api/parties", json=_party_payload(), headers=auth_header(host_token)
    ).json()

    # role 변경
    client.patch(
        f"/api/admin/users/{target['id']}/role",
        json={"role": "admin"},
        headers=auth_header(admin_token),
    )
    # 활성 상태 변경
    client.patch(
        f"/api/admin/users/{target['id']}/status",
        json={"is_active": False},
        headers=auth_header(admin_token),
    )
    # 파티 상태 변경
    client.patch(
        f"/api/admin/parties/{party['id']}/status",
        json={"status": "canceled", "admin_note": "테스트 취소"},
        headers=auth_header(admin_token),
    )

    res = client.get("/api/admin/actions", headers=auth_header(admin_token))
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 4
    types = {item["action_type"] for item in body["items"]}
    assert types == {"admin_login", "user_role_update", "user_status_update", "party_status_update"}
    # 최신순 + 필드 확인
    latest = body["items"][0]
    assert latest["action_type"] == "party_status_update"
    assert latest["before_value"] == "recruiting"
    assert latest["after_value"] == "canceled"
    assert latest["note"] == "테스트 취소"
    assert latest["actor_admin_name"] == "관리자"


def test_admin_actions_filter_by_type(client):
    _, admin_token = _make_admin()
    target, _ = register_and_login(client, "t2@yonsei.ac.kr")
    client.patch(
        f"/api/admin/users/{target['id']}/role",
        json={"role": "admin"},
        headers=auth_header(admin_token),
    )
    client.patch(
        f"/api/admin/users/{target['id']}/status",
        json={"is_active": False},
        headers=auth_header(admin_token),
    )

    res = client.get(
        "/api/admin/actions?action_type=user_role_update",
        headers=auth_header(admin_token),
    )
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["action_type"] == "user_role_update"
    assert body["items"][0]["target_type"] == "user"
    assert body["items"][0]["target_id"] == target["id"]


def test_admin_actions_requires_admin(client):
    _, token = register_and_login(client, "n2@yonsei.ac.kr")
    assert client.get("/api/admin/actions").status_code == 401
    assert client.get(
        "/api/admin/actions", headers=auth_header(token)
    ).status_code == 403


# ──────────────────────────────────────────────────────────────
# 마스터 관리자 규칙 (명세 §3주차 보완)
# ──────────────────────────────────────────────────────────────


def test_role_change_requires_master_admin(client):
    """일반 admin(비마스터)이 role 변경 시도 → 403 MASTER_ADMIN_REQUIRED."""
    _, normal_admin_token = _make_admin("normaladmin@yonsei.ac.kr")  # 마스터 아님
    target, _ = register_and_login(client, "rtarget@yonsei.ac.kr")
    res = client.patch(
        f"/api/admin/users/{target['id']}/role",
        json={"role": "admin"},
        headers=auth_header(normal_admin_token),
    )
    assert res.status_code == 403
    assert res.json()["error_code"] == "MASTER_ADMIN_REQUIRED"


def test_master_admin_role_cannot_be_changed(client):
    """마스터 관리자 대상 role 변경 → 409 MASTER_ADMIN_PROTECTED."""
    master, master_token = _make_admin()  # admin@yonsei.ac.kr = 마스터
    res = client.patch(
        f"/api/admin/users/{master['id']}/role",
        json={"role": "user"},
        headers=auth_header(master_token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "MASTER_ADMIN_PROTECTED"


def test_master_admin_cannot_be_deactivated(client):
    """마스터 관리자 비활성화 → 409 MASTER_ADMIN_PROTECTED."""
    master, master_token = _make_admin()
    res = client.patch(
        f"/api/admin/users/{master['id']}/status",
        json={"is_active": False},
        headers=auth_header(master_token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "MASTER_ADMIN_PROTECTED"


def test_me_includes_master_admin_flag(client):
    """AUTH-003(me)·사용자 목록 응답에 master_admin 필드 포함 (명세 §3주차 보완)."""
    _, master_token = _make_admin()
    res = client.get("/api/auth/me", headers=auth_header(master_token))
    assert res.status_code == 200
    assert res.json()["master_admin"] is True

    _, normal_token = register_and_login(client, "plain@yonsei.ac.kr")
    res2 = client.get("/api/auth/me", headers=auth_header(normal_token))
    assert res2.json()["master_admin"] is False
