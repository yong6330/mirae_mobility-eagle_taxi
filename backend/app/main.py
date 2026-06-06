"""독수리 택시 백엔드 진입점.

실행:
    uvicorn app.main:app --reload

Swagger UI: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
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
