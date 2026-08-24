"""Typed request contracts for the public, versioned API."""
from typing import Any
from pydantic import BaseModel, Field, field_validator


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class EvidenceSubmission(BaseModel):
    task_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,79}$")
    evidence_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,79}$")
    value: Any

    @field_validator("value")
    @classmethod
    def evidence_must_be_bounded(cls, value: Any) -> Any:
        import json
        if len(json.dumps(value, sort_keys=True)) > 8192:
            raise ValueError("evidence value must be 8 KiB or smaller")
        return value


class RegistrationRequest(BaseModel):
    email: str = Field(max_length=320)
    password: str = Field(min_length=12, max_length=256)


class LoginRequest(RegistrationRequest):
    pass


class TokenRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class PasswordResetRequest(BaseModel):
    email: str = Field(max_length=320)


class PasswordResetConfirm(TokenRequest):
    password: str = Field(min_length=12, max_length=256)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=12, max_length=256)


class ProfilePatch(BaseModel):
    target_difficulty: str | None = Field(default=None, pattern=r"^(beginner|intermediate|advanced)$")
    learning_pace: str | None = Field(default=None, pattern=r"^(light|steady|intensive)$")
    experience_level: str | None = Field(default=None, pattern=r"^(novice|beginner|intermediate|advanced)$")


class GoalSelection(BaseModel):
    goal_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    is_primary: bool = False


class ProgressUpdate(BaseModel):
    entity_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,159}$")
    status: str = Field(pattern=r"^(not-started|in-progress|completed)$")
    confidence: str = Field(default="unknown", pattern=r"^(unknown|low|medium|high)$")


class BookmarkCreate(BaseModel):
    entity_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,159}$")


class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=20000)
    entity_id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9-]{0,159}$")


class NotePatch(BaseModel):
    body: str | None = Field(default=None, min_length=1, max_length=20000)
    entity_id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9-]{0,159}$")
