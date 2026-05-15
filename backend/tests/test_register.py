"""POST /api/auth/register 통합 테스트 — 기능명세서 F-AUTH-001."""


def test_health_response_matches_spec(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "eagle-taxi-api"}


def test_register_returns_message_and_user(client):
    res = client.post(
        "/api/auth/register",
        json={
            "email": "test@yonsei.ac.kr",
            "password": "password1234",
            "name": "이가람",
            "gender": "male",
        },
    )
    assert res.status_code == 201, res.text

    body = res.json()
    assert body["message"] == "회원가입이 완료되었습니다."

    user = body["user"]
    assert set(user.keys()) == {"id", "email", "name", "gender", "role", "created_at"}
    assert user["email"] == "test@yonsei.ac.kr"
    assert user["role"] == "user"

    assert "password" not in res.text
    assert "password_hash" not in res.text


def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dup@yonsei.ac.kr", "password": "password1234", "name": "홍길동"}
    assert client.post("/api/auth/register", json=payload).status_code == 201

    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    assert res.json()["detail"] == "이미 가입된 이메일입니다."


def test_register_email_is_case_insensitive(client):
    p1 = {"email": "Same@Yonsei.AC.kr", "password": "password1234", "name": "A"}
    p2 = {"email": "same@yonsei.ac.kr", "password": "password1234", "name": "B"}
    assert client.post("/api/auth/register", json=p1).status_code == 201
    assert client.post("/api/auth/register", json=p2).status_code == 409


def test_register_invalid_email_format_returns_400_with_korean_message(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "not-an-email", "password": "password1234", "name": "홍길동"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "이메일 형식에 맞춰 입력해주세요."


def test_register_password_too_short_returns_400(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "short@yonsei.ac.kr", "password": "1234", "name": "홍길동"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "비밀번호 형식이 올바르지 않습니다."


def test_register_invalid_gender_value_returns_400(client):
    res = client.post(
        "/api/auth/register",
        json={
            "email": "g@yonsei.ac.kr",
            "password": "password1234",
            "name": "홍길동",
            "gender": "unknown",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "성별 값이 올바르지 않습니다."


def test_register_missing_field_returns_400(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "miss@yonsei.ac.kr", "password": "password1234"},  # name 누락
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "필수 항목을 입력해주세요."
