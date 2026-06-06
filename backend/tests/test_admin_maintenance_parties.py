"""관리자 파티 유지보수 API 테스트 — ADMIN-018~023 (요청서 2026-06-04)."""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import User
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


def _create_payload(creator_id: int, **overrides) -> dict:
    base = {
        "creator_user_id": creator_id,
        "start_place": "연세대학교 미래캠퍼스",
        "start_lat": 37.341,
        "start_lng": 127.918,
        "end_place": "원주역",
        "end_lat": 37.337,
        "end_lng": 127.945,
        "departure_time": (now_kst_naive() + timedelta(hours=3)).isoformat(),
        "meeting_point": "정문",
        "max_members": 4,
        "gender_rule": "any",
        "admin_note": "관리자 생성",
    }
    base.update(overrides)
    return base


# ── ADMIN-018 생성 ──────────────────────────────────────────


def test_admin_create_party_success(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c@yonsei.ac.kr")
    res = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["party"]["creator_id"] == creator["id"]
    assert body["party"]["current_members"] == 1
    assert len(body["party"]["members"]) == 1
    assert isinstance(body["admin_action_id"], int)


def test_admin_create_party_invalid_capacity(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c2@yonsei.ac.kr")
    res = client.post(
        "/api/admin/parties",
        json=_create_payload(creator["id"], max_members=5),
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert res.json()["error_code"] == "ADMIN_PARTY_CAPACITY_INVALID"


def test_admin_create_party_with_initial_members(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c3@yonsei.ac.kr")
    m2, _ = register_and_login(client, "m2@yonsei.ac.kr")
    res = client.post(
        "/api/admin/parties",
        json=_create_payload(creator["id"], initial_member_ids=[creator["id"], m2["id"]]),
        headers=auth_header(token),
    )
    assert res.status_code == 201, res.text
    assert res.json()["party"]["current_members"] == 2


# ── ADMIN-019 수정 ──────────────────────────────────────────


def test_admin_update_party_success(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c4@yonsei.ac.kr")
    party = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    ).json()["party"]
    res = client.patch(
        f"/api/admin/parties/{party['id']}",
        json={"meeting_point": "후문", "max_members": 3, "admin_note": "수정"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["party"]["meeting_point"] == "후문"
    assert res.json()["party"]["max_members"] == 3


def test_admin_update_party_new_creator_must_be_member(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c5@yonsei.ac.kr")
    outsider, _ = register_and_login(client, "out@yonsei.ac.kr")
    party = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    ).json()["party"]
    res = client.patch(
        f"/api/admin/parties/{party['id']}",
        json={"creator_user_id": outsider["id"], "admin_note": "생성자 변경"},
        headers=auth_header(token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "ADMIN_PARTY_MEMBER_NOT_FOUND"


# ── ADMIN-020 삭제 ──────────────────────────────────────────


def test_admin_delete_party_soft(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c6@yonsei.ac.kr")
    party = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    ).json()["party"]

    res = client.request(
        "DELETE",
        f"/api/admin/parties/{party['id']}",
        json={"admin_note": "중복 정리"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["deleted"] is True
    # 일반 목록에서 제외
    listing = client.get("/api/parties", headers=auth_header(token)).json()
    assert all(p["id"] != party["id"] for p in listing["parties"])


# ── ADMIN-021 상태 복구 ─────────────────────────────────────


def test_admin_status_recover_to_recruiting(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c7@yonsei.ac.kr")
    party = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    ).json()["party"]
    # 취소
    client.patch(
        f"/api/admin/parties/{party['id']}/status",
        json={"status": "canceled", "admin_note": "취소"},
        headers=auth_header(token),
    )
    # 복구
    res = client.patch(
        f"/api/admin/parties/{party['id']}/status",
        json={"status": "recruiting", "admin_note": "오취소 복구"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "recruiting"


# ── ADMIN-022 참여자 추가 / ADMIN-023 삭제 ──────────────────


def test_admin_add_and_remove_member(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c8@yonsei.ac.kr")
    newbie, _ = register_and_login(client, "nb@yonsei.ac.kr")
    party = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    ).json()["party"]

    # 추가
    add = client.post(
        f"/api/admin/parties/{party['id']}/members",
        json={"user_id": newbie["id"], "admin_note": "오프라인 요청"},
        headers=auth_header(token),
    )
    assert add.status_code == 201, add.text
    assert add.json()["party"]["current_members"] == 2

    # 중복 추가 → 409
    dup = client.post(
        f"/api/admin/parties/{party['id']}/members",
        json={"user_id": newbie["id"], "admin_note": "중복"},
        headers=auth_header(token),
    )
    assert dup.status_code == 409
    assert dup.json()["error_code"] == "ADMIN_PARTY_MEMBER_ALREADY_EXISTS"

    # 삭제
    rem = client.request(
        "DELETE",
        f"/api/admin/parties/{party['id']}/members/{newbie['id']}",
        json={"admin_note": "취소 반영"},
        headers=auth_header(token),
    )
    assert rem.status_code == 200, rem.text
    assert rem.json()["party"]["current_members"] == 1


def test_admin_remove_creator_blocked(client):
    _, token = _master_admin()
    creator, _ = register_and_login(client, "c9@yonsei.ac.kr")
    party = client.post(
        "/api/admin/parties", json=_create_payload(creator["id"]), headers=auth_header(token)
    ).json()["party"]
    res = client.request(
        "DELETE",
        f"/api/admin/parties/{party['id']}/members/{creator['id']}",
        json={"admin_note": "생성자 제거 시도"},
        headers=auth_header(token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "ADMIN_PARTY_STATUS_TRANSITION_INVALID"
