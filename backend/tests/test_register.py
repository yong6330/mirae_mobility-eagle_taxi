"""POST /api/auth/register 통합 테스트 — 명세서 v0.4 F-AUTH-001."""


def test_health_response_matches_spec(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "eagle-taxi-api"}


def test_register_returns_user_object_directly(client):
    """v0.4: 응답은 user 객체를 직접 반환 (래퍼 없음)."""
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
    assert set(body.keys()) == {
        "id", "email", "name", "gender", "role", "is_active", "master_admin", "created_at"
    }
    assert body["email"] == "test@yonsei.ac.kr"
    assert body["name"] == "이가람"
    assert body["gender"] == "male"
    assert body["role"] == "user"
    assert body["is_active"] is True
    assert body["master_admin"] is False

    assert "password" not in res.text
    assert "password_hash" not in res.text


def test_register_duplicate_email_returns_409(client):
    payload = {
        "email": "dup@yonsei.ac.kr",
        "password": "password1234",
        "name": "홍길동",
        "gender": "female",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 201

    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    assert res.json()["detail"] == "이미 가입된 이메일입니다."


def test_register_email_is_case_insensitive(client):
    p1 = {"email": "Same@Yonsei.AC.kr", "password": "password1234", "name": "A", "gender": "male"}
    p2 = {"email": "same@yonsei.ac.kr", "password": "password1234", "name": "B", "gender": "male"}
    assert client.post("/api/auth/register", json=p1).status_code == 201
    assert client.post("/api/auth/register", json=p2).status_code == 409


def test_register_invalid_email_format_returns_400_with_korean_message(client):
    res = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "password1234",
            "name": "홍길동",
            "gender": "male",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "이메일 형식에 맞춰 입력해주세요."


def test_register_password_too_short_returns_400(client):
    res = client.post(
        "/api/auth/register",
        json={
            "email": "short@yonsei.ac.kr",
            "password": "1234",
            "name": "홍길동",
            "gender": "male",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "비밀번호 형식이 올바르지 않습니다."


def test_register_invalid_gender_value_returns_400(client):
    """v0.4: gender는 male/female만. unknown 거부."""
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


def test_register_gender_none_rejected(client):
    """v0.4: gender=none도 회원가입 단계에서 거부."""
    res = client.post(
        "/api/auth/register",
        json={
            "email": "none@yonsei.ac.kr",
            "password": "password1234",
            "name": "홍길동",
            "gender": "none",
        },
    )
    assert res.status_code == 400


def test_register_missing_gender_returns_400_with_specific_message(client):
    """v0.4 AUTH-001: gender 미선택 시 '성별을 선택해주세요.'"""
    res = client.post(
        "/api/auth/register",
        json={
            "email": "miss@yonsei.ac.kr",
            "password": "password1234",
            "name": "홍길동",
        },
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "성별을 선택해주세요."


def test_register_missing_other_field_returns_400(client):
    """gender 외 필수 항목 누락 시 '필수 항목을 입력해주세요.'"""
    res = client.post(
        "/api/auth/register",
        json={"email": "miss2@yonsei.ac.kr", "password": "password1234", "gender": "male"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "필수 항목을 입력해주세요."
