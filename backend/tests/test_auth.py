"""로그인 / 내 정보 조회 — 기능명세서 F-AUTH-002, F-AUTH-003."""

from tests.conftest import auth_header, register_and_login


def test_login_success_returns_token_and_user(client):
    client.post(
        "/api/auth/register",
        json={"email": "a@yonsei.ac.kr", "password": "password1234", "name": "A", "gender": "male"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "a@yonsei.ac.kr", "password": "password1234"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20
    assert body["user"]["email"] == "a@yonsei.ac.kr"


def test_login_wrong_password_returns_401(client):
    client.post(
        "/api/auth/register",
        json={"email": "a@yonsei.ac.kr", "password": "password1234", "name": "A"},
    )
    res = client.post(
        "/api/auth/login",
        json={"email": "a@yonsei.ac.kr", "password": "wrongpassword"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."


def test_login_unknown_email_returns_401(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "nobody@yonsei.ac.kr", "password": "password1234"},
    )
    assert res.status_code == 401


def test_me_returns_current_user(client):
    user, token = register_and_login(client, "me@yonsei.ac.kr")
    res = client.get("/api/auth/me", headers=auth_header(token))
    assert res.status_code == 200
    assert res.json()["email"] == user["email"]


def test_me_without_token_returns_401(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
    assert res.json()["detail"] == "로그인이 필요합니다."


def test_me_with_invalid_token_returns_401(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401
