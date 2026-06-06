"""독수리 택시 백엔드 진입점.

실행:
    uvicorn app.main:app --reload

Swagger UI: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.exceptions import register_exception_handlers
from app.models import *  # noqa: F401, F403  -- import 자체로 모든 모델을 Base.metadata에 등록
from app.routers import admin, auth, chat_ws, fares, health, messages, my_parties, party, support


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작 시 테이블이 없으면 생성한다. (Alembic 도입 전 임시 방식)"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="독수리 택시 API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def access_log_middleware(request: Request, call_next):
    """통합 런처 접속자 표시용 HTTP 접근 로그.

    Cloudflare Tunnel / Vite proxy / 로컬 접속 환경에서 가능한 IP 후보를 순서대로 확인한다.

    우선순위:
    1. CF-Connecting-IP      : Cloudflare가 전달하는 원본 접속자 IP
    2. X-Forwarded-For       : 프록시 체인의 원본 IP 후보
    3. X-Real-IP             : 일부 프록시가 전달하는 원본 IP
    4. request.client.host   : FastAPI가 직접 본 클라이언트 IP

    출력 형식:
        [ACCESS] ip=... method=... path=... status=... elapsed_ms=...
    """
    started_at = time.time()

    cf_ip = request.headers.get("cf-connecting-ip")
    forwarded_for = request.headers.get("x-forwarded-for")
    real_ip = request.headers.get("x-real-ip")

    client_ip = (
        cf_ip
        or (forwarded_for.split(",")[0].strip() if forwarded_for else None)
        or real_ip
        or (request.client.host if request.client else "unknown")
    )

    response = await call_next(request)

    elapsed_ms = int((time.time() - started_at) * 1000)

    print(
        f"[ACCESS] "
        f"ip={client_ip} "
        f"method={request.method} "
        f"path={request.url.path} "
        f"status={response.status_code} "
        f"elapsed_ms={elapsed_ms}"
    )

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def register_routers() -> None:
    """라우터 등록 — 새 라우터 추가 시 여기에 한 줄만 더하면 된다."""
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(party.router)
    app.include_router(fares.router)
    app.include_router(my_parties.router)
    app.include_router(messages.router)
    app.include_router(chat_ws.router)
    app.include_router(support.router)
    app.include_router(support.admin_router)
    app.include_router(admin.router)


register_routers()
register_exception_handlers(app)