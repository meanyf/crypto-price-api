# crud.py
from app.schemas.user import User, UserInDB

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
