"""Typed request contracts for the public, versioned API."""
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class CommunityRequest(BaseModel):
    """Reject undeclared browser fields such as role, status, or reputation."""
    model_config = ConfigDict(extra="forbid")


class CommunityProfileCreate(CommunityRequest):
    username: str = Field(pattern=r"^[a-z0-9_]{3,40}$")
    display_name: str | None = Field(default=None, max_length=80)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = Field(default=None, max_length=512)
    website_url: str | None = Field(default=None, max_length=512)
    github_username: str | None = Field(default=None, pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
    is_public: bool = False


class CommunityProfilePatch(CommunityRequest):
    display_name: str | None = Field(default=None, max_length=80)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = Field(default=None, max_length=512)
    website_url: str | None = Field(default=None, max_length=512)
    github_username: str | None = Field(default=None, pattern=r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
    is_public: bool | None = None


class ContributionCreate(CommunityRequest):
    contribution_type: str = Field(pattern=r"^(tool|vulnerability|concept|technique|technology|defensive-control|lab|learning-path|relationship|source|verification-correction|content-correction|broken-link)$")
    title: str = Field(min_length=4, max_length=180)
    description: str = Field(min_length=1, max_length=8000)
    proposed_data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("proposed_data")
    @classmethod
    def proposal_data_is_bounded(cls, value: dict[str, Any]) -> dict[str, Any]:
        import json
        if len(json.dumps(value, sort_keys=True)) > 32768:
            raise ValueError("proposed content must be 32 KiB or smaller")
        return value


class ContributionPatch(CommunityRequest):
    title: str | None = Field(default=None, min_length=4, max_length=180)
    description: str | None = Field(default=None, min_length=1, max_length=8000)
    proposed_data: dict[str, Any] | None = None
    summary: str = Field(min_length=3, max_length=500)

    @field_validator("proposed_data")
    @classmethod
    def patch_data_is_bounded(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return value
        return ContributionCreate.proposal_data_is_bounded(value)


class ContributionSubmit(CommunityRequest):
    confirmation: bool


class ReviewActionRequest(CommunityRequest):
    action: str = Field(pattern=r"^(changes-requested|reviewer-approved|rejected|duplicate|maintainer-approved|merged|published)$")
    reason: str = Field(min_length=3, max_length=2000)


class ReviewCommentCreate(CommunityRequest):
    body: str = Field(min_length=1, max_length=4000)


class CommunityReportCreate(CommunityRequest):
    report_type: str = Field(pattern=r"^(incorrect-information|unsafe-content|broken-link|wrong-relationship|duplicate|outdated|copyright-concern|security-concern|other)$")
    entity_id: str | None = Field(default=None, pattern=r"^[a-z0-9][a-z0-9-]{0,159}$")
    description: str = Field(min_length=4, max_length=4000)


class ReportResolution(CommunityRequest):
    status: str = Field(pattern=r"^(triaged|investigating|resolved|dismissed|duplicate)$")
    resolution: str = Field(min_length=3, max_length=2000)


class UserModerationRequest(CommunityRequest):
    status: str = Field(pattern=r"^(active|suspended)$")
    reason: str = Field(min_length=3, max_length=2000)


class RoleAssignmentRequest(CommunityRequest):
    role: str = Field(pattern=r"^(contributor|reviewer|maintainer|administrator)$")
    reason: str = Field(min_length=3, max_length=2000)


class GithubHandoffRequest(CommunityRequest):
    confirmation: bool
    reason: str = Field(min_length=3, max_length=1000)


class ReviewerAssignmentRequest(CommunityRequest):
    reviewer_id: str = Field(pattern=r"^[0-9a-f-]{36}$")
    reason: str = Field(min_length=3, max_length=2000)
