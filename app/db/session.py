# session.py
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

engine = create_engine(
    settings.sqlalchemy_database_uri, future=True, pool_pre_ping=True
)
SessionLocal = sessionmaker(
    bind=engine, autoflush=True, expire_on_commit=False, future=True
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
