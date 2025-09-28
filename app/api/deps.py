# deps.py
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import JWTError, jwt
from app.core.security import oauth2_scheme
from app.db.session import fake_users_db
from app.db.crud import get_user
from app.schemas.user import User, UserInDB
from app.schemas.token import Token, TokenData
from app.core.config import settings
from jwt.exceptions import InvalidTokenError

async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(oauth2_scheme)] = None,
    access_token: str = Cookie(None),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Приоритет: куки > заголовок Authorization
    token_to_use = access_token or token

    if not token_to_use:
        raise credentials_exception

    try:
        payload = jwt.decode(
            token_to_use, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


