# crud.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User

def get_user(db: Session, username: str) -> User | None:
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()


def create_user(db: Session, *, username: str, password: str) -> User:
    from app.core.security import get_password_hash
    user = User(username=username, password=get_password_hash(password))
    db.add(user)
    db.flush()  # user.id уже доступен
    return user
