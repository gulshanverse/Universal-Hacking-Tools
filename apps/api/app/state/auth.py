"""Private account, opaque-session, CSRF, and token lifecycle helpers."""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi import Cookie, Depends, Header, HTTPException, Request, Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .config import settings
from .database import database_ready, get_db, sessions
from .models import PasswordResetToken, SessionRecord, User, VerificationToken, utcnow

PASSWORDS = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1, hash_len=32, salt_len=16)
EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
COMMON_PASSWORDS = {"password", "password123", "123456789012", "qwertyuiop", "letmein12345"}
TOKEN_BYTES = 32


@dataclass(frozen=True)
class Principal:
    user: User
    session: SessionRecord


def now() -> datetime:
    return datetime.now(timezone.utc)


def expired(value: datetime) -> bool:
    comparable = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return comparable <= now()


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if len(email) > 320 or not EMAIL.fullmatch(email):
        raise ValueError("provide a valid email address")
    return email


def validate_password(value: str) -> str:
    if len(value) < 12 or len(value) > 256 or value.casefold() in COMMON_PASSWORDS:
        raise ValueError("password does not meet the security policy")
    return value


def password_hash(value: str) -> str:
    return PASSWORDS.hash(validate_password(value))


def verify_password(stored: str, supplied: str) -> bool:
    try:
        return PASSWORDS.verify(stored, supplied)
    except (VerifyMismatchError, InvalidHashError):
        return False


def random_token() -> str:
    return secrets.token_urlsafe(TOKEN_BYTES)


def token_hash(token: str, purpose: str) -> str:
    secret = settings().session_secret if purpose == "session" else settings().csrf_secret
    return hmac.new(secret.encode("utf-8"), f"{purpose}:{token}".encode("utf-8"), hashlib.sha256).hexdigest()


def valid_token(row_hash: str, token: str, purpose: str) -> bool:
    return hmac.compare_digest(row_hash, token_hash(token, purpose))


def issue_session(db: Session, user: User, response: Response) -> SessionRecord:
    config = settings()
    raw_session, raw_csrf = random_token(), random_token()
    session = SessionRecord(
        user_id=user.id,
        token_hash=token_hash(raw_session, "session"),
        csrf_hash=token_hash(raw_csrf, "csrf"),
        expires_at=now() + timedelta(seconds=config.session_ttl_seconds),
    )
    db.add(session)
    db.flush()
    cookie_options = {"httponly": True, "secure": config.secure_cookies, "samesite": "lax", "path": "/", "max_age": config.session_ttl_seconds}
    response.set_cookie("uht_session", raw_session, **cookie_options)
    response.set_cookie("uht_csrf", raw_csrf, httponly=False, secure=config.secure_cookies, samesite="lax", path="/", max_age=config.session_ttl_seconds)
    return session


def clear_session_cookies(response: Response) -> None:
    response.delete_cookie("uht_session", path="/")
    response.delete_cookie("uht_csrf", path="/")


def _principal(db: Session, raw_session: str | None) -> Principal:
    if not raw_session:
        raise HTTPException(status_code=401, detail="authentication is required")
    row = db.scalar(select(SessionRecord).where(SessionRecord.token_hash == token_hash(raw_session, "session")))
    if not row or row.revoked_at or expired(row.expires_at) or expired(row.last_seen_at + timedelta(seconds=settings().session_idle_seconds)):
        raise HTTPException(status_code=401, detail="authentication is required")
    user = db.get(User, row.user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="authentication is required")
    row.last_seen_at = now()
    db.flush()
    return Principal(user=user, session=row)


def current_principal(db: Session = Depends(get_db), raw_session: str | None = Cookie(default=None, alias="uht_session")) -> Principal:
    return _principal(db, raw_session)


def optional_principal(db: Session = Depends(get_db), raw_session: str | None = Cookie(default=None, alias="uht_session")) -> Principal | None:
    if not raw_session:
        return None
    try:
        return _principal(db, raw_session)
    except HTTPException:
        return None


def csrf_protected(
    request: Request,
    principal: Principal = Depends(current_principal),
    raw_csrf: str | None = Cookie(default=None, alias="uht_csrf"),
    header_csrf: str | None = Header(default=None, alias="X-CSRF-Token"),
) -> Principal:
    origin = request.headers.get("origin")
    allowed = [item.strip() for item in request.app.state.allowed_origins]
    if origin and origin not in allowed:
        raise HTTPException(status_code=403, detail="cross-origin request rejected")
    if not raw_csrf or not header_csrf or not hmac.compare_digest(raw_csrf, header_csrf) or not valid_token(principal.session.csrf_hash, raw_csrf, "csrf"):
        raise HTTPException(status_code=403, detail="csrf validation failed")
    return principal


def optional_mutation_user_id(raw_session: str | None, raw_csrf: str | None, header_csrf: str | None) -> str | None:
    """Return an authenticated user only after CSRF validation; anonymous Phase 6 labs remain local-only."""
    if not raw_session:
        return None
    if not database_ready():
        raise HTTPException(status_code=503, detail="private application state is temporarily unavailable")
    db = sessions()()
    try:
        principal = _principal(db, raw_session)
        if not raw_csrf or not header_csrf or not hmac.compare_digest(raw_csrf, header_csrf) or not valid_token(principal.session.csrf_hash, raw_csrf, "csrf"):
            raise HTTPException(status_code=403, detail="csrf validation failed")
        return principal.user.id
    finally:
        db.close()


def revoke_all(db: Session, user_id: str) -> None:
    db.execute(update(SessionRecord).where(SessionRecord.user_id == user_id, SessionRecord.revoked_at.is_(None)).values(revoked_at=now()))


def one_time_token(db: Session, user_id: str, kind: str) -> str:
    model = VerificationToken if kind == "verify" else PasswordResetToken
    raw = random_token()
    row = model(user_id=user_id, token_hash=token_hash(raw, kind), expires_at=now() + timedelta(minutes=30))
    db.add(row)
    db.flush()
    return raw


def consume_token(db: Session, raw: str, kind: str) -> User | None:
    model = VerificationToken if kind == "verify" else PasswordResetToken
    row = db.scalar(select(model).where(model.token_hash == token_hash(raw, kind)))
    if not row or row.used_at or expired(row.expires_at) or not valid_token(row.token_hash, raw, kind):
        return None
    row.used_at = now()
    return db.get(User, row.user_id)
