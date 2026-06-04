"""관리자 사용자 유지보수 API 테스트 — ADMIN-013 ~ 016 (요청서 2026-06-04)."""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.main import app
from app.models import User
from app.utils.time import now_kst_naive
from tests.conftest import auth_header, register_and_login


def _master_admin(email: str = "admin@yonsei.ac.kr") -> tuple[dict, str]:
    """마스터 관리자 토큰 — conftest의 MASTER_ADMIN_EMAILS=admin@yonsei.ac.kr 기준."""
    c = TestClient(app)
    user, token = register_and_login(c, email, name="관리자")
    with SessionLocal() as db:
        u = db.execute(select(User).where(User.email == email)).scalar_one()
        u.role = "admin"
        db.commit()
    return user, token


def _party_payload(**overrides) -> dict:
    base = {
        "start_place": "연세대학교 미래캠퍼스",
        "start_lat": 37.341,
        "start_lng": 127.918,
        "end_place": "원주역",
        "end_lat": 37.337,
        "end_lng": 127.945,
        "departure_time": (now_kst_naive() + timedelta(hours=2)).isoformat(),
        "meeting_point": "정문",
        "max_members": 4,
        "gender_rule": "any",
    }
    base.update(overrides)
    return base


# ── ADMIN-013 생성 ──────────────────────────────────────────


def test_admin_create_user_success(client):
    _, token = _master_admin()
    res = client.post(
        "/api/admin/users",
        json={
            "email": "new@yonsei.ac.kr",
            "password": "password1234",
            "name": "신규",
            "gender": "female",
            "admin_note": "시연 계정 생성",
        },
        headers=auth_header(token),
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user"]["email"] == "new@yonsei.ac.kr"
    assert body["user"]["role"] == "user"
    assert "password" not in res.text and "password_hash" not in res.text
    assert isinstance(body["admin_action_id"], int)


def test_admin_create_user_requires_note(client):
    _, token = _master_admin()
    res = client.post(
        "/api/admin/users",
        json={"email": "n2@yonsei.ac.kr", "password": "password1234", "name": "x", "gender": "male"},
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert res.json()["error_code"] == "ADMIN_NOTE_REQUIRED"


def test_admin_create_user_duplicate_email(client):
    _, token = _master_admin()
    register_and_login(client, "dup@yonsei.ac.kr")
    res = client.post(
        "/api/admin/users",
        json={
            "email": "dup@yonsei.ac.kr",
            "password": "password1234",
            "name": "중복",
            "gender": "male",
            "admin_note": "테스트",
        },
        headers=auth_header(token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "AUTH_EMAIL_ALREADY_EXISTS"


def test_admin_create_user_requires_master(client):
    # 일반 admin(비마스터)은 403
    _, normal_token = _master_admin("normaladmin@yonsei.ac.kr")  # 마스터 아님
    res = client.post(
        "/api/admin/users",
        json={
            "email": "x3@yonsei.ac.kr",
            "password": "password1234",
            "name": "x",
            "gender": "male",
            "admin_note": "n",
        },
        headers=auth_header(normal_token),
    )
    assert res.status_code == 403
    assert res.json()["error_code"] == "MASTER_ADMIN_REQUIRED"


# ── ADMIN-014 수정 ──────────────────────────────────────────


def test_admin_update_user_success(client):
    _, token = _master_admin()
    target, _ = register_and_login(client, "u@yonsei.ac.kr")
    res = client.patch(
        f"/api/admin/users/{target['id']}",
        json={"name": "수정됨", "role": "admin", "admin_note": "권한 부여"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["user"]["name"] == "수정됨"
    assert body["user"]["role"] == "admin"


def test_admin_update_master_admin_protected(client):
    master, token = _master_admin()
    res = client.patch(
        f"/api/admin/users/{master['id']}",
        json={"role": "user", "admin_note": "시도"},
        headers=auth_header(token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "MASTER_ADMIN_PROTECTED"


# ── ADMIN-015 비밀번호 초기화 ───────────────────────────────


def test_admin_password_reset_success(client):
    _, token = _master_admin()
    target, _ = register_and_login(client, "pw@yonsei.ac.kr", password="oldpass1234")
    res = client.post(
        f"/api/admin/users/{target['id']}/password-reset",
        json={"new_password": "newpass1234", "admin_note": "초기화"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["password_reset"] is True
    # 새 비번으로 로그인 가능
    ok = client.post("/api/auth/login", json={"email": "pw@yonsei.ac.kr", "password": "newpass1234"})
    assert ok.status_code == 200


def test_admin_password_reset_policy_fail(client):
    _, token = _master_admin()
    target, _ = register_and_login(client, "pw2@yonsei.ac.kr")
    res = client.post(
        f"/api/admin/users/{target['id']}/password-reset",
        json={"new_password": "short", "admin_note": "초기화"},
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert res.json()["error_code"] == "ADMIN_PASSWORD_POLICY_FAILED"


# ── ADMIN-016 삭제 ──────────────────────────────────────────


def test_admin_delete_user_soft(client):
    _, token = _master_admin()
    target, target_token = register_and_login(client, "del@yonsei.ac.kr")
    res = client.request(
        "DELETE",
        f"/api/admin/users/{target['id']}",
        json={"delete_mode": "soft", "admin_note": "테스트 계정 정리"},
        headers=auth_header(token),
    )
    assert res.status_code == 200, res.text
    assert res.json()["deleted"] is True
    # 삭제된 사용자는 로그인 불가
    relog = client.post("/api/auth/login", json={"email": "del@yonsei.ac.kr", "password": "password1234"})
    assert relog.status_code == 401


def test_admin_delete_user_with_active_party_blocked(client):
    _, token = _master_admin()
    target, target_token = register_and_login(client, "host@yonsei.ac.kr")
    # 활성 파티 생성(생성자 자동 참여)
    client.post("/api/parties", json=_party_payload(), headers=auth_header(target_token))

    res = client.request(
        "DELETE",
        f"/api/admin/users/{target['id']}",
        json={"admin_note": "삭제 시도"},
        headers=auth_header(token),
    )
    assert res.status_code == 409
    assert res.json()["error_code"] == "ADMIN_USER_HAS_ACTIVE_PARTIES"


def test_admin_delete_user_requires_note(client):
    _, token = _master_admin()
    target, _ = register_and_login(client, "del2@yonsei.ac.kr")
    res = client.request(
        "DELETE",
        f"/api/admin/users/{target['id']}",
        json={"delete_mode": "soft"},
        headers=auth_header(token),
    )
    assert res.status_code == 400
    assert res.json()["error_code"] == "ADMIN_NOTE_REQUIRED"
