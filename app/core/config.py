# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "JWT App"
    DEBUG: bool = False

    # JWT
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_EXPIRE_MINUTES: int


    class Config:
        env_file = ".env"


settings = Settings()
