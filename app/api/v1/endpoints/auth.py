# auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel

from app.schemas.creds_schema import Creds
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.services.auth_service import login_user, register_user, make_token_for_user, get_cookie_from_token
from fastapi.templating import Jinja2Templates
from fastapi import Request

auth_router = APIRouter(prefix="/auth", tags=["auth"])


templates = Jinja2Templates(directory="templates")


@auth_router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


from typing import Annotated
from fastapi import APIRouter, Depends, Response, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    creds: Creds, 
):
    user = login_user(db, creds.username, creds.password.get_secret_value())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token, expires = make_token_for_user(user)

    response.set_cookie(**get_cookie_from_token(token, expires))
    print(creds)
    return {"token": token}


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    creds: Creds,  
):
    user = register_user(db, creds.username, creds.password.get_secret_value())
    token, expires = make_token_for_user(user)
    response.set_cookie(**get_cookie_from_token(token, expires))
    return {"token": token}
