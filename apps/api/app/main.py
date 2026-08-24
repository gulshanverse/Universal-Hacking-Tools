"""Versioned API entrypoint over immutable generated repository contracts."""
from __future__ import annotations
from pathlib import Path
import os
import sys
import uuid
from time import perf_counter

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .models.contracts import ErrorResponse
from .services.artifacts import ArtifactNotReady
from .services.labs import LabNotExecutable
from .services.rate_limit import RateLimitExceeded
from .routers import auth, community, private, v1
from .state.config import settings, validate_production_secrets
from .state.observability import configure_logging, duration_ms, request_id


CONFIG = settings()
API_VERSION = CONFIG.build_version
logger = configure_logging(os.getenv("UHT_LOG_LEVEL", "INFO"))

app = FastAPI(
    title="Universal Hacking Tools Knowledge API",
    version=API_VERSION,
    description="Versioned, local-first API over deterministic generated knowledge contracts, strictly bounded graph intelligence, and proposal-only community collaboration. Community routes never mutate canonical knowledge; Git and maintainer review remain the publication boundary. Lab routes accept only predefined safe local-fixture actions; arbitrary commands and target scanning are not supported.",
    openapi_url="/openapi.json",
    docs_url="/docs" if CONFIG.enable_docs else None,
)
app.state.allowed_origins = CONFIG.allowed_origins
app.state.build_version = CONFIG.build_version
app.state.build_commit = CONFIG.build_commit
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(CONFIG.trusted_hosts))
app.add_middleware(CORSMiddleware, allow_origins=list(CONFIG.allowed_origins), allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Content-Type", "X-Lab-Session", "X-CSRF-Token", "X-Request-ID"], max_age=600)


@app.on_event("startup")
async def validate_runtime_configuration() -> None:
    validate_production_secrets()
    logger.info("runtime configuration validated", extra={"event": "startup", "environment": CONFIG.environment})

@app.middleware("http")
async def security_headers(request: Request, call_next):
    start = perf_counter()
    correlation_id = request_id(request.headers.get("x-request-id"))
    if len(str(request.url)) > CONFIG.max_url_length:
        response = error("URL_TOO_LONG", "request URL exceeds the configured limit", 414)
        response.headers["X-Request-ID"] = correlation_id
        return response
    if sum(len(name) + len(value) for name, value in request.headers.items()) > CONFIG.max_header_bytes:
        response = error("HEADERS_TOO_LARGE", "request headers exceed the configured limit", 431)
        response.headers["X-Request-ID"] = correlation_id
        return response
    content_length = request.headers.get("content-length")
    try:
        declared_length = int(content_length) if content_length else 0
    except ValueError:
        declared_length = CONFIG.max_request_bytes + 1
    if declared_length > CONFIG.max_request_bytes or request.headers.get("transfer-encoding"):
        response = error("REQUEST_TOO_LARGE", "request body exceeds the configured limit", 413)
        response.headers["X-Request-ID"] = correlation_id
        return response
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Request-ID"] = correlation_id
    if CONFIG.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.url.path.startswith(("/api/v1/me", "/api/v1/community/", "/api/v1/auth")) or "uht_session" in request.cookies:
        response.headers["Cache-Control"] = "private, no-store"
    logger.info("request complete", extra={"event": "request", "request_id": correlation_id, "route": request.url.path, "method": request.method, "status": response.status_code, "duration_ms": duration_ms(start), "environment": CONFIG.environment})
    return response


def error(code: str, message: str, status_code: int, details: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message, "details": details or {}}})


@app.exception_handler(ArtifactNotReady)
async def artifact_error(_: Request, exc: ArtifactNotReady):
    return error("ARTIFACT_NOT_READY", "generated knowledge artifacts are not ready", 503)


@app.exception_handler(RateLimitExceeded)
async def rate_error(_: Request, exc: RateLimitExceeded):
    return error("RATE_LIMITED", str(exc), 429)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError):
    issues = [{"location": ".".join(str(value) for value in item.get("loc", ())), "type": item.get("type", "invalid"), "message": item.get("msg", "invalid value")} for item in exc.errors()]
    return error("INVALID_PARAMETER", "request parameters are invalid", 422, {"issues": issues})


@app.exception_handler(HTTPException)
async def http_error(_: Request, exc: HTTPException):
    status_to_code = {401: "AUTHENTICATION_REQUIRED", 403: "ACCESS_DENIED", 404: "ENTITY_NOT_FOUND", 409: "INVALID_LAB_STATE", 422: "INVALID_PARAMETER", 503: "APPLICATION_STATE_UNAVAILABLE"}
    message = exc.detail if isinstance(exc.detail, str) else "request could not be completed"
    return error(status_to_code.get(exc.status_code, "REQUEST_REJECTED"), message, exc.status_code)


@app.exception_handler(LabNotExecutable)
async def lab_not_executable(_: Request, exc: LabNotExecutable):
    return error("LAB_NOT_EXECUTABLE", str(exc), 409)


@app.exception_handler(ValueError)
async def value_error(_: Request, exc: ValueError):
    message = str(exc)
    code = "INVALID_LAB_STATE" if "transition" in message or "running state" in message else "INVALID_PARAMETER"
    if "unknown instance" in message:
        code = "LAB_INSTANCE_NOT_FOUND"
    if "unknown entity" in message or "unknown lab" in message:
        code = "ENTITY_NOT_FOUND"
    return error(code, message, 400 if code == "INVALID_PARAMETER" else 404 if code in {"ENTITY_NOT_FOUND", "LAB_INSTANCE_NOT_FOUND"} else 409)


@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception):
    logger.error("unhandled request error", extra={"event": "error", "environment": CONFIG.environment})
    return error("INTERNAL_ERROR", "the request could not be completed", 500)


app.include_router(v1.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(private.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")
