import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str = Field(...)
    SECRET_KEY: str = Field(...)
    GRPC_TARGET: str = Field(...)
    REDIS_URL: str = "redis://localhost:6379/0"   # ← new, with safe default

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    CACHE_TTL_SECONDS: int = 60                    # ← new


settings = Settings()