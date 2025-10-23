# crud.py
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.models import User, Crypto

def get_user(db: Session, username: str) -> User | None:
    return db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()


def create_user(db: Session, *, username: str, password: str) -> User:
    from app.core.security import get_password_hash
    user = User(username=username, password=get_password_hash(password))
    db.add(user)
    return user


def create_crypto(db: Session, *, crypto_name: str) -> Crypto:
    crypto = User(crypto_name=crypto_name)
    db.add(crypto)
    return crypto
