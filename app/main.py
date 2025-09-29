# main.py

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi.responses import HTMLResponse
import jwt
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32
from app.core.config import settings

from app.api.v1.api import api_router
from app.core.security import get_password_hash

app = FastAPI()
app.include_router(api_router)
print(get_password_hash("secret"))
print('DFRTGYHUOJFEFEFEWFEWFEFEWFEWFEW')