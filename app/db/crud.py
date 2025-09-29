# crud.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User

def get_user(db: Session, username: str) -> User | None:
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
