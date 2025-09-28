# auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel

from app.core.security import authenticate_user, create_access_token
from app.db.session import fake_users_db
from app.core.config import settings
from app.schemas.user import User, UserInDB
from app.schemas.token import Token, TokenData

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"msg": "Logged out"}

from fastapi.templating import Jinja2Templates
from fastapi import Request


templates = Jinja2Templates(directory="templates")


@auth_router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@auth_router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Устанавливаем cookie с токеном
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # localhost иначе не примет
        samesite="lax",  # вместо "none"
        max_age=int(settings.ACCESS_EXPIRE_MINUTES * 60),
        path="/",
    )

    # По-прежнему возвращаем тело ответа с токеном (опционально)
    return Token(access_token=access_token, token_type="bearer")
