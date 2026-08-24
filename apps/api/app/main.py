"""Phase 7 local-first API entrypoint over immutable generated repository contracts."""
from __future__ import annotations
from pathlib import Path
import os
import sys
import uuid

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .models.contracts import ErrorResponse
from .services.artifacts import ArtifactNotReady
from .services.labs import LabNotExecutable
from .services.rate_limit import RateLimitExceeded
from .routers import auth, private, v1
from .state.config import validate_production_secrets


API_VERSION = "8.0.0"
MAX_REQUEST_BYTES = int(os.getenv("UHT_MAX_REQUEST_BYTES", "65536"))
allowed_origins = [item.strip() for item in os.getenv("UHT_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if item.strip()]

app = FastAPI(
    title="Universal Hacking Tools Knowledge API",
    version=API_VERSION,
    description="Versioned, local-first API over deterministic generated knowledge contracts. Lab routes accept only predefined safe local-fixture actions; arbitrary commands and target scanning are not supported.",
    openapi_url="/openapi.json",
    docs_url="/docs",
)
app.state.allowed_origins = allowed_origins
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], allow_headers=["Content-Type", "X-Lab-Session", "X-CSRF-Token"])


@app.on_event("startup")
async def validate_phase8_configuration() -> None:
    validate_production_secrets()


@app.middleware("http")
async def security_headers(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BYTES:
        return JSONResponse(status_code=413, content={"error": {"code": "REQUEST_TOO_LARGE", "message": "request body exceeds the configured limit", "details": {}}})
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-Frame-Options"] = "DENY"
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
    return error("INVALID_PARAMETER", "request parameters are invalid", 422, {"issues": exc.errors()})


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
    return error("INTERNAL_ERROR", "the request could not be completed", 500)


app.include_router(v1.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(private.router, prefix="/api/v1")
