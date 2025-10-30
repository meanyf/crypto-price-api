# crud.py
from typing import List
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


def create_crypto(db: Session, crypto_dict: dict) -> Crypto:
    crypto = Crypto(**crypto_dict)
    db.add(crypto)
    return crypto


def get_cryptos(db: Session) -> List[Crypto]:
    return db.execute(select(Crypto)).scalars().all()


def get_crypto(db: Session, crypto_symbol: str) -> List[Crypto]:
    return db.execute(
        select(Crypto).where(Crypto.symbol == crypto_symbol)
    ).scalar_one_or_none()
