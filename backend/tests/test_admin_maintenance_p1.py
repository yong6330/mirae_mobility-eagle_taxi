"""관리자 유지보수 P1 테스트 — ADMIN-017/024/025/026/027 (요청서 2026-06-04)."""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import Message, User
from app.utils.time import now_kst_naive
from tests.conftest import auth_header, register_and_login


def _master_admin(email: str = "admin@yonsei.ac.kr") -> tuple[dict, str]:
    c = TestClient(app)
    user, token = register_and_login(c, email, name="관리자")
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.role = "admin"
        db.commit()
    return user, token


def _create_party(client, token, creator_id, **overrides):
    payload = {
        "creator_user_id": creator_id,
        "start_place": "연세대학교 미래캠퍼스",
        "start_lat": 37.341,
        "start_lng": 127.918,
        "end_place": "원주역",
        "end_lat": 37.337,
        "end_lng": 127.945,
        "departure_time": (now_kst_naive() + timedelta(hours=3)).isoformat(),
        "max_members": 4,
        "gender_rule": "any",
        "admin_note": "생성",
    }
    payload.update(overrides)
    return client.post("/api/admin/parties", json=payload, headers=auth_header(token)).json()["party"]


# ── ADMIN-017 사용자 파티 이력 ──────────────────────────────


def test_admin_user_parties(client):
    _, token = _master_admin()
    user, _ = register_and_login(client, "uu@yonsei.ac.kr")
    _create_party(client, token, user["id"])
    res = client.get(f"/api/admin/users/{user['id']}/parties", headers=auth_header(token))
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["relation"] == "created"


# ── ADMIN-024 요금 재산정 ───────────────────────────────────


def test_admin_recalculate_fare(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "rf@yonsei.ac.kr")
    party = _create_party(client, token, creator["id"])
    res = client.post(
        f"/api/admin/parties/{party['id']}/fare/recalculate",
        json={"admin_note": "경로 수정 후 재산정"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["party"]["fare_source"] in ("kakao_mobility", "fallback")


# ── ADMIN-025 요금 수동 보정 ────────────────────────────────


def test_admin_override_fare(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "of@yonsei.ac.kr")
    party = _create_party(client, token, creator["id"])
    res = client.patch(
        f"/api/admin/parties/{party['id']}/fare",
        json={
            "estimated_fare": 18000,
            "distance_meters": 12500,
            "duration_seconds": 1800,
            "admin_note": "시연 보정",
        },
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    body = res.json()["party"]
    assert body["estimated_fare"] == 18000
    assert body["fare_source"] == "admin_override"
    assert body["per_person_fare"] == 18000  # 1명


def test_admin_override_fare_requires_note(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "of2@yonsei.ac.kr")
    party = _create_party(client, token, creator["id"])
    res = client.patch(
        f"/api/admin/parties/{party['id']}/fare",
        json={"estimated_fare": 1000, "distance_meters": 100, "duration_seconds": 100},
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert res.json()["error_code"] == "ADMIN_NOTE_REQUIRED"


# ── ADMIN-026 메시지 숨김 ───────────────────────────────────


def test_admin_hide_message(client):
    _, token = _master_admin()
    creator, creator_token = register_and_login(client, "mh@yonsei.ac.kr")
    party = _create_party(client, token, creator["id"])
    with SessionLocal() as db:
        m = Message(party_id=party["id"], user_id=creator["id"], content="숨길 메시지")
        db.add(m)
        db.commit()
        msg_id = m.id

    res = client.request(
        "DELETE",
        f"/api/admin/messages/{msg_id}",
        json={"admin_note": "테스트 메시지 정리"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["hidden"] is True

    # 채팅 목록(참여자)에서 제외
    chat = client.get(
        f"/api/parties/{party['id']}/messages", headers=auth_header(creator_token)
    ).json()
    assert all(item["id"] != msg_id for item in chat["items"])

    # 중복 숨김 → 409
    dup = client.request(
        "DELETE",
        f"/api/admin/messages/{msg_id}",
        json={"admin_note": "다시"},
        headers=auth_header(token),
    )
    assert dup.status_code == 409
    assert dup.json()["error_code"] == "MESSAGE_ALREADY_HIDDEN"


def test_admin_hide_message_not_found(client):
    _, token = _master_admin()
    res = client.request(
        "DELETE",
        "/api/admin/messages/99999",
        json={"admin_note": "x"},
        headers=auth_header(token),
    )
    assert res.status_code == 404
    assert res.json()["error_code"] == "MESSAGE_NOT_FOUND"


# ── ADMIN-027 공지 메시지 ───────────────────────────────────


def test_admin_create_notice(client):
    _, token = _master_admin()
    creator, creator_token = register_and_login(client, "nt@yonsei.ac.kr")
    party = _create_party(client, token, creator["id"])
    res = client.post(
        f"/api/admin/parties/{party['id']}/messages/notice",
        json={"content": "관리자 안내: 출발 시간 변경", "admin_note": "공지"},
        headers=auth_header(token),
    )
    assert res.status_code == 201, res.text
    assert res.json()["message"]["is_admin_notice"] is True

    # 참여자 채팅 목록에 공지가 노출됨
    chat = client.get(
        f"/api/parties/{party['id']}/messages", headers=auth_header(creator_token)
    ).json()
    assert any("출발 시간 변경" in item["content"] for item in chat["items"])
