"""Private Phase 8 account lifecycle routes; public knowledge routes remain in v1."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.contracts import ChangePasswordRequest, LoginRequest, PasswordResetConfirm, PasswordResetRequest, RegistrationRequest, TokenRequest
from ..services.email_service import email_service
from ..services.rate_limit import LocalRateLimiter
from ..state.auth import Principal, clear_session_cookies, consume_token, csrf_protected, current_principal, issue_session, normalize_email, one_time_token, optional_principal, password_hash, revoke_all, validate_password, verify_password
from ..state.database import get_db
from ..state.models import User, UserProfile, utcnow

router = APIRouter(prefix="/auth", tags=["authenticated"])
auth_limiter = LocalRateLimiter(limit=8, window_seconds=600)


def rate_guard(request: Request) -> None:
    auth_limiter.check(f"auth:{request.client.host if request.client else 'local'}:{request.url.path}")


def public_user(user: User) -> dict:
    return {"id": user.id, "status": user.status, "email_verified": bool(user.email_verified_at), "created_at": user.created_at}


@router.post("/register", status_code=202, summary="Register a pending-verification account")
def register(payload: RegistrationRequest, request: Request, db: Session = Depends(get_db), _: None = Depends(rate_guard)):
    try:
        email, password = normalize_email(payload.email), validate_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    existing = db.scalar(select(User).where(User.email == email))
    if not existing:
        user = User(email=email, password_hash=password_hash(password))
        db.add(user); db.flush(); db.add(UserProfile(user_id=user.id)); db.flush()
        email_service.send_verification(email, one_time_token(db, user.id, "verify"))
        db.commit()
    return {"message": "If registration can be completed, verification instructions will be available through the configured delivery channel."}


@router.post("/verify-email", summary="Consume a single-use email verification token")
def verify_email(payload: TokenRequest, db: Session = Depends(get_db), _: None = Depends(rate_guard)):
    user = consume_token(db, payload.token, "verify")
    if not user:
        raise HTTPException(status_code=400, detail="verification token is invalid or expired")
    user.status, user.email_verified_at = "active", utcnow()
    db.commit()
    return {"message": "email verification completed"}


@router.post("/login", summary="Create an opaque authenticated session")
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db), _: None = Depends(rate_guard)):
    try:
        email = normalize_email(payload.email)
    except ValueError:
        email = ""
    user = db.scalar(select(User).where(User.email == email)) if email else None
    if not user or user.status != "active" or not verify_password(user.password_hash, payload.password):
        raise HTTPException(status_code=401, detail="credentials could not be accepted")
    user.last_login_at = utcnow(); issue_session(db, user, response); db.commit()
    return {"user": public_user(user), "csrf_required": True}


@router.post("/logout", summary="Revoke the current authenticated session")
def logout(response: Response, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    principal.session.revoked_at = utcnow(); db.commit(); clear_session_cookies(response)
    return {"message": "signed out"}


@router.post("/logout-all", summary="Revoke every account session")
def logout_all(response: Response, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    revoke_all(db, principal.user.id); db.commit(); clear_session_cookies(response)
    return {"message": "all sessions were signed out"}


@router.get("/session", summary="Read safe current session state")
def session_state(principal: Principal | None = Depends(optional_principal)):
    if not principal:
        return {"authenticated": False}
    return {"authenticated": True, "user": public_user(principal.user), "csrf_required": True}


@router.post("/request-password-reset", status_code=202, summary="Request a generic password reset")
def request_reset(payload: PasswordResetRequest, request: Request, db: Session = Depends(get_db), _: None = Depends(rate_guard)):
    try:
        email = normalize_email(payload.email)
    except ValueError:
        email = ""
    user = db.scalar(select(User).where(User.email == email, User.status == "active")) if email else None
    if user:
        email_service.send_password_reset(user.email, one_time_token(db, user.id, "reset")); db.commit()
    return {"message": "If an account is eligible, reset instructions will be available through the configured delivery channel."}


@router.post("/reset-password", summary="Reset a password and revoke existing sessions")
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db), _: None = Depends(rate_guard)):
    try:
        password = validate_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    user = consume_token(db, payload.token, "reset")
    if not user:
        raise HTTPException(status_code=400, detail="reset token is invalid or expired")
    user.password_hash = password_hash(password); revoke_all(db, user.id); db.commit()
    return {"message": "password reset completed"}
