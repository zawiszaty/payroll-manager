from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    PROJECT_NAME: str = "Payroll Manager"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str
    RABBITMQ_URL: str
    RABBITMQ_EXCHANGE_EMPLOYEE: str = "employee.events"
    RABBITMQ_EXCHANGE_CONTRACT: str = "contract.events"
    REDIS_URL: str

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
