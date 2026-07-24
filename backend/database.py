"""SQLite 엔진·세션 유틸."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

engine = create_engine(
    "sqlite:///app.db",
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    """정의된 SQLModel 테이블을 생성한다."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """트랜잭션 세션을 제공한다."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_session() -> Iterator[Session]:
    """FastAPI Depends용 세션 생성기."""
    with Session(engine) as session:
        yield session
