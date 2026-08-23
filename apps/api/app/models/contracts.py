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
