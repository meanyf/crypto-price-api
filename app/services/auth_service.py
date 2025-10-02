# auth_service.py

from sqlalchemy.orm import Session
from app.db.models import User
from app.db.crud import get_user, create_user
from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, Response, HTTPException, status
from app.core.config import settings
from app.core.security import authenticate_user, create_access_token
from datetime import datetime, timedelta, timezone

def register_user(db: Session, username: str, password: str) -> User:
    if get_user(db, username):
        raise ValueError("Username already exists")

    user = create_user(db, username=username, password=password)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, username: str, password: str) -> User:
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def make_token_for_user(user: User) -> tuple[str, timedelta]:
    expires = timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.username}, expires_delta=expires)
    return token, expires


def get_cookie_from_token(token: str, expires: timedelta) -> dict:
    return {
        "key": "access_token",
        "value": token,
        "httponly": True,
        "secure": not settings.DEBUG,  # secure=True в проде
        "samesite": "lax",  # или 'none' при cross-site и HTTPS
        "max_age": int(expires.total_seconds()),
        "path": "/",
    }

