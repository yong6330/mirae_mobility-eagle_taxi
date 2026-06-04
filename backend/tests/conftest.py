"""테스트 공통 설정 — DB 격리, 인증된 클라이언트 헬퍼."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_eagle_taxi.db")
# 테스트의 기본 관리자(admin@yonsei.ac.kr)를 마스터 관리자로 취급한다.
# ADMIN-006(role 변경)은 마스터 전용이므로 테스트 actor가 마스터여야 한다.
os.environ.setdefault("MASTER_ADMIN_EMAILS", "admin@yonsei.ac.kr")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def register_and_login(
    client: TestClient,
    email: str,
    password: str = "password1234",
    name: str = "테스터",
    gender: str = "male",  # 명세서 v0.4: male/female 필수
) -> tuple[dict, str]:
    """회원가입 후 로그인까지 수행하고 (user_info, access_token)을 반환한다."""
    client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "name": name, "gender": gender},
    )
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    body = res.json()
    return body["user"], body["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
