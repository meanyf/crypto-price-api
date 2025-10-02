# security.py
from datetime import datetime, timedelta, timezone
from fastapi import Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from app.core.config import settings
from app.db import crud
from sqlalchemy.orm import Session


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str | None:
        # сначала пробуем куку
        token = request.cookies.get("access_token")
        if token:
            return token
        # иначе используем стандартный поиск (Authorization header / form body)
        return await super().__call__(request)


# from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user
