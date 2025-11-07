# deps.py
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import JWTError, jwt
from app.core.security import oauth2_scheme
from app.db.session import get_db
from app.db import crud
from app.schemas.token_schema import Token, TokenData
from app.core.config import settings
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import sessionmaker, Session
from app.schemas.user_schema import UserOut


async def get_current_user(
    db: Annotated[Session, Depends(get_db)],  
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
    access_token: str = Cookie(None),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_to_use = access_token or token
    if not token_to_use:
        raise credentials_exception

    try:
        payload = jwt.decode(token_to_use, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            print('nouser')
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        print('tokenerror')
        raise credentials_exception
    user = crud.get_user(db, username=token_data.username)   # <-- передаём db
    if user is None:
        raise credentials_exception
    return UserOut.model_validate(user)

from fastapi import Request
from app.ports.coingecko_port import CoingeckoPort
from app.ports.cache_port import CachePort


def get_coingecko_client(request: Request) -> CoingeckoPort:
    return request.app.state.coingecko


def get_cache_client(request: Request) -> CachePort:
    return request.app.state.cache

from app.services.crypto_service import CryptoService
def get_crypto_service(
    db: Session = Depends(get_db),
    coingecko: CoingeckoPort = Depends(get_coingecko_client),
    cache: CachePort = Depends(get_cache_client),
) -> CryptoService:
    return CryptoService(db=db, coingecko=coingecko, cache=cache)
