# users.py
from typing import Annotated
from fastapi import APIRouter, Depends
from app.schemas.user import User
from app.api.deps import get_current_user

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user

