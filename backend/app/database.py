"""SQLAlchemy 엔진·세션·Base 정의.

라우터에서 DB가 필요할 때는 `Depends(get_db)`를 통해 세션을 주입받는다.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite는 기본적으로 같은 connection을 여러 스레드에서 못 쓰게 막는다.
# FastAPI는 요청마다 다른 스레드를 쓰므로 이 제약을 풀어준다.
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=_connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """모든 SQLAlchemy 모델의 부모 클래스."""


def get_db():
    """요청 단위로 DB 세션을 열고, 끝나면 닫는다. FastAPI Depends 용도."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
