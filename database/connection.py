from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = None


def init_engine(database_url: str):
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(database_url, future=True, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine


@contextmanager
def session_scope():
    if SessionLocal is None:
        raise RuntimeError("La base de datos no ha sido inicializada. Ejecuta init_engine primero.")
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
