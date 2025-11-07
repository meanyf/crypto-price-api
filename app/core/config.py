# config.py
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "JWT App"
    DEBUG: bool = False

    # JWT
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_EXPIRE_MINUTES: int

    # Postgres
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: Optional[str] = None

    @property
    def sqlalchemy_database_uri(self) -> str:
        # кэшируем в приватном атрибуте экземпляра, чтобы вычислить только единожды
        cached: Optional[str] = getattr(self, "_sqlalchemy_database_uri", None)
        if cached is not None:
            return cached

        uri = f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        # сохраняем в экземпляре
        object.__setattr__(self, "_sqlalchemy_database_uri", uri)
        return uri

    @property
    def redis_url(self) -> str:
        """
        Возвращаем REDIS_URL если установлен, иначе строим из полей.
        """
        cached: Optional[str] = getattr(self, "_redis_url", None)
        if cached is not None:
            return cached

        # если нужен пароль — добавляем :password@ в URL
        pass_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        url = f"redis://{pass_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

        object.__setattr__(self, "_redis_url", url)
        return url

    class Config:
        env_file = ".env"


settings = Settings()
