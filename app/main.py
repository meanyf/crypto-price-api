# main.py

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi.responses import HTMLResponse, JSONResponse
import jwt
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import DomainError

# app = FastAPI()
from app.factory import create_app

app = create_app()

from app.api.v1.api import api_router

from app.api.v1.errors import register_exception_handlers
register_exception_handlers(app)

app.include_router(api_router)
