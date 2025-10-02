# auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel

from app.core.security import authenticate_user, create_access_token
from app.core.config import settings
from app.schemas.token import Token, TokenData
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.services.auth_service import login_user, register_user, make_token_for_user, get_cookie_from_token


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


@auth_router.post("/login")
async def login(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = login_user(db, form_data.username, form_data.password)
    token, expires = make_token_for_user(user)
    response.set_cookie(**get_cookie_from_token(token, expires))


@auth_router.post("/register")
async def register(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = register_user(db, form_data.username, form_data.password)
    token, expires = make_token_for_user(user)
    response.set_cookie(**get_cookie_from_token(token, expires))
