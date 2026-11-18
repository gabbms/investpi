from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

def argumentos_engine() -> dict:
    """pre_ping refaz conexões que a Neon fechou ao adormecer; sem prepared statements, que o
    pooler da Neon (PgBouncer) pode não reconhecer entre conexões."""
    return {"pool_pre_ping": True, "connect_args": {"prepare_threshold": None}}


engine = create_engine(settings.DATABASE_URL, **argumentos_engine())
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
