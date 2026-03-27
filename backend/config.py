from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "5000"))
    app_debug: bool = os.getenv("APP_DEBUG", "true").lower() == "true"
    app_secret_key: str = os.getenv("APP_SECRET_KEY", "change-me-in-env")
    default_username: str = os.getenv("APP_DEFAULT_USERNAME", "irvingag")
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "10"))
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/sga",
    )
    encryption_key: str = os.getenv("APP_ENCRYPTION_KEY", "")


settings = Settings()
