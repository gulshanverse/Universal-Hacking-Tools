"""Environment-only configuration with explicit production safety checks."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


ENVIRONMENTS = frozenset({"development", "test", "staging", "production"})
UNSAFE_SECRET_MARKERS = ("development", "changeme", "change-me", "replace-with", "password")


def _environment() -> str:
    value = os.getenv("UHT_ENVIRONMENT", "development").strip().lower()
    if value not in ENVIRONMENTS:
        raise RuntimeError("UHT_ENVIRONMENT must be development, test, staging, or production")
    return value


def _boolean(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized not in {"true", "false"}:
        raise RuntimeError(f"{name} must be true or false")
    return normalized == "true"


def _positive_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise RuntimeError(f"{name} must be between {minimum} and {maximum}")
    return value


def _items(name: str, default: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in os.getenv(name, default).split(",") if item.strip())


def _validate_origin(value: str, *, production: bool) -> None:
    parsed = urlsplit(value)
    if value == "*" or not parsed.scheme or not parsed.netloc or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise RuntimeError("UHT_ALLOWED_ORIGINS must contain explicit origin URLs only")
    if production and parsed.scheme != "https":
        raise RuntimeError("production allowed origins must use HTTPS")


def _validate_host(value: str) -> None:
    if value in {"*", ""} or "/" in value or "://" in value:
        raise RuntimeError("UHT_TRUSTED_HOSTS must contain explicit host names only")


@dataclass(frozen=True)
class StateSettings:
    environment: str
    database_url: str
    lab_state_dir: str
    session_secret: str
    csrf_secret: str
    session_ttl_seconds: int
    session_idle_seconds: int
    secure_cookies: bool
    allowed_origins: tuple[str, ...]
    trusted_hosts: tuple[str, ...]
    max_request_bytes: int
    max_url_length: int
    max_header_bytes: int
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout_seconds: int
    database_statement_timeout_ms: int
    enable_docs: bool
    build_version: str
    build_commit: str

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


def settings() -> StateSettings:
    environment = _environment()
    production = environment == "production"
    origins = _items("UHT_ALLOWED_ORIGINS", "" if production else "http://localhost:3000,http://127.0.0.1:3000")
    hosts = _items("UHT_TRUSTED_HOSTS", "" if production else "localhost,127.0.0.1,testserver")
    for origin in origins:
        _validate_origin(origin, production=production)
    for host in hosts:
        _validate_host(host)
    return StateSettings(
        environment=environment,
        database_url=os.getenv("DATABASE_URL", "" if production else "postgresql+psycopg://uht:uht@127.0.0.1:5432/uht"),
        lab_state_dir=os.getenv("UHT_LAB_STATE_DIR", "" if production else "/tmp/uht-api-labs"),
        session_secret=os.getenv("SESSION_SECRET", "" if production else "development-only-change-me"),
        csrf_secret=os.getenv("CSRF_SECRET", "" if production else "development-only-change-me"),
        session_ttl_seconds=_positive_int("UHT_SESSION_TTL_SECONDS", 60 * 60 * 24 * 14, minimum=300, maximum=60 * 60 * 24 * 90),
        session_idle_seconds=_positive_int("UHT_SESSION_IDLE_SECONDS", 60 * 60 * 24, minimum=300, maximum=60 * 60 * 24 * 30),
        secure_cookies=_boolean("UHT_SECURE_COOKIES", production),
        allowed_origins=origins,
        trusted_hosts=hosts,
        max_request_bytes=_positive_int("UHT_MAX_REQUEST_BYTES", 65536, minimum=1024, maximum=1048576),
        max_url_length=_positive_int("UHT_MAX_URL_LENGTH", 2048, minimum=256, maximum=8192),
        max_header_bytes=_positive_int("UHT_MAX_HEADER_BYTES", 16384, minimum=1024, maximum=65536),
        database_pool_size=_positive_int("UHT_DATABASE_POOL_SIZE", 5, minimum=1, maximum=50),
        database_max_overflow=_positive_int("UHT_DATABASE_MAX_OVERFLOW", 5, minimum=0, maximum=50),
        database_pool_timeout_seconds=_positive_int("UHT_DATABASE_POOL_TIMEOUT_SECONDS", 30, minimum=1, maximum=300),
        database_statement_timeout_ms=_positive_int("UHT_DATABASE_STATEMENT_TIMEOUT_MS", 30000, minimum=1000, maximum=300000),
        enable_docs=_boolean("UHT_ENABLE_DOCS", not production),
        build_version=os.getenv("UHT_BUILD_VERSION", "11.0.0").strip() or "11.0.0",
        build_commit=os.getenv("UHT_BUILD_COMMIT", "unknown").strip() or "unknown",
    )


def validate_production_secrets() -> None:
    value = settings()
    if not value.is_production:
        return
    if not value.database_url or not value.database_url.startswith("postgresql"):
        raise RuntimeError("production DATABASE_URL must use a configured PostgreSQL connection")
    if not value.lab_state_dir or not Path(value.lab_state_dir).is_absolute():
        raise RuntimeError("production UHT_LAB_STATE_DIR must be an explicit absolute local-fixture state path")
    if not value.allowed_origins or not value.trusted_hosts:
        raise RuntimeError("production origins and trusted hosts must be explicitly configured")
    if not value.secure_cookies:
        raise RuntimeError("production cookies must be secure")
    for name, secret in (("SESSION_SECRET", value.session_secret), ("CSRF_SECRET", value.csrf_secret)):
        normalized = secret.casefold()
        if len(secret) < 32 or any(marker in normalized for marker in UNSAFE_SECRET_MARKERS):
            raise RuntimeError(f"production {name} must be a long random non-placeholder value")
