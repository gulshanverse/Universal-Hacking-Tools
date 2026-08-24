"""Environment-only configuration for private application state."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class StateSettings:
    environment: str
    database_url: str
    session_secret: str
    csrf_secret: str
    session_ttl_seconds: int
    session_idle_seconds: int
    secure_cookies: bool

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


def settings() -> StateSettings:
    environment = os.getenv("UHT_ENVIRONMENT", "development")
    secure = os.getenv("UHT_SECURE_COOKIES", "true" if environment == "production" else "false").lower() == "true"
    return StateSettings(
        environment=environment,
        database_url=os.getenv("DATABASE_URL", "postgresql+psycopg://uht:uht@127.0.0.1:5432/uht"),
        session_secret=os.getenv("SESSION_SECRET", "development-only-change-me"),
        csrf_secret=os.getenv("CSRF_SECRET", "development-only-change-me"),
        session_ttl_seconds=int(os.getenv("UHT_SESSION_TTL_SECONDS", str(60 * 60 * 24 * 14))),
        session_idle_seconds=int(os.getenv("UHT_SESSION_IDLE_SECONDS", str(60 * 60 * 24))),
        secure_cookies=secure,
    )


def validate_production_secrets() -> None:
    value = settings()
    if value.is_production and (value.session_secret == "development-only-change-me" or value.csrf_secret == "development-only-change-me"):
        raise RuntimeError("production session and CSRF secrets must be configured")
