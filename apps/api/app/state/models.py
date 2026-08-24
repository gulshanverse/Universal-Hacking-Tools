"""Private application-state schema; canonical cybersecurity knowledge remains Git-generated."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def uid() -> str:
    return str(uuid4())


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending-verification", nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    role: Mapped[str] = mapped_column(String(32), default="contributor", nullable=False)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint("status IN ('active','suspended','pending-verification','deleted')", name="ck_users_status"),
        CheckConstraint("role IN ('contributor','reviewer','maintainer','administrator')", name="ck_users_role"),
    )


class SessionRecord(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    csrf_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class VerificationToken(Base):
    __tablename__ = "email_verification_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    target_difficulty: Mapped[str] = mapped_column(String(32), default="beginner", nullable=False)
    learning_pace: Mapped[str] = mapped_column(String(32), default="steady", nullable=False)
    experience_level: Mapped[str] = mapped_column(String(32), default="novice", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class LearningGoal(Base):
    __tablename__ = "learning_goals"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    learning_path_id: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)


class UserLearningGoal(Base):
    __tablename__ = "user_learning_goals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id: Mapped[str] = mapped_column(ForeignKey("learning_goals.id", ondelete="RESTRICT"), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "goal_id", name="uq_user_goal"), Index("ix_user_goals_user", "user_id"))


class EntityProgress(Base):
    __tablename__ = "entity_progress"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    knowledge_version: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="not-started", nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), default="unknown", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "entity_id", name="uq_entity_progress"), Index("ix_entity_progress_user_entity", "user_id", "entity_id"), CheckConstraint("status IN ('not-started','in-progress','completed','mastered')", name="ck_progress_status"))


class LearningPathProgress(Base):
    __tablename__ = "learning_path_progress"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learning_path_id: Mapped[str] = mapped_column(String(128), nullable=False)
    knowledge_version: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="not-started", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("user_id", "learning_path_id", name="uq_learning_path_progress"),)


class LabAttempt(Base):
    __tablename__ = "lab_attempts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lab_id: Mapped[str] = mapped_column(String(128), nullable=False)
    knowledge_version: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="started", nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("user_id", "lab_id", "attempt_number", name="uq_lab_attempt_number"), Index("ix_lab_attempt_user_lab", "user_id", "lab_id"), CheckConstraint("status IN ('started','completed','failed','abandoned')", name="ck_lab_attempt_status"))


class LabTaskProgress(Base):
    __tablename__ = "lab_task_progress"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    attempt_id: Mapped[str] = mapped_column(ForeignKey("lab_attempts.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("attempt_id", "task_id", name="uq_lab_task_progress"),)


class Bookmark(Base):
    __tablename__ = "bookmarks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(160), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "entity_id", name="uq_bookmark"), Index("ix_bookmark_user", "user_id"))


class PrivateNote(Base):
    __tablename__ = "private_notes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    __table_args__ = (Index("ix_private_note_user", "user_id"), CheckConstraint("length(body) <= 20000", name="ck_note_size"))


class Achievement(Base):
    __tablename__ = "achievements"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    criteria: Mapped[dict] = mapped_column(JSON, nullable=False)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id: Mapped[str] = mapped_column(ForeignKey("achievements.id", ondelete="RESTRICT"), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"), Index("ix_user_achievement_user", "user_id"))


class RecommendationSnapshot(Base):
    __tablename__ = "recommendation_snapshots"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    knowledge_version: Mapped[str] = mapped_column(String(128), nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_recommendation_snapshot_user", "user_id"),)


class CommunityProfile(Base):
    """Opt-in public contributor metadata; never a second knowledge profile."""
    __tablename__ = "community_profiles"
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(80))
    bio: Mapped[str | None] = mapped_column(String(1000))
    avatar_url: Mapped[str | None] = mapped_column(String(512))
    website_url: Mapped[str | None] = mapped_column(String(512))
    github_username: Mapped[str | None] = mapped_column(String(39))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("length(username) >= 3 AND length(username) <= 40", name="ck_community_username_length"),
        CheckConstraint("username = lower(username)", name="ck_community_username_normalized"),
    )


class Contribution(Base):
    """Untrusted proposal state only. proposed_data never becomes canonical knowledge directly."""
    __tablename__ = "contributions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    contribution_type: Mapped[str] = mapped_column(String(48), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    validation: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    duplicate_candidates: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    impact: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    assigned_reviewer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewer_recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    github_issue_url: Mapped[str | None] = mapped_column(String(512))
    github_pr_url: Mapped[str | None] = mapped_column(String(512))
    github_commit_sha: Mapped[str | None] = mapped_column(String(64))
    github_handoff_status: Mapped[str | None] = mapped_column(String(24))
    knowledge_version_before: Mapped[str | None] = mapped_column(String(128))
    knowledge_version_after: Mapped[str | None] = mapped_column(String(128))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("contribution_type IN ('tool','vulnerability','concept','technique','technology','defensive-control','lab','learning-path','relationship','source','verification-correction','content-correction','broken-link')", name="ck_contribution_type"),
        CheckConstraint("status IN ('draft','submitted','validation-failed','queued','under-review','changes-requested','approved','rejected','withdrawn','merged','published')", name="ck_contribution_status"),
        CheckConstraint("github_handoff_status IS NULL OR github_handoff_status IN ('queued','failed','created')", name="ck_contribution_handoff_status"),
        Index("ix_contribution_status_created", "status", "created_at"),
        Index("ix_contribution_type_created", "contribution_type", "created_at"),
        Index("ix_contribution_assigned_reviewer", "assigned_reviewer_id", "status"),
    )


class ContributionVersion(Base):
    __tablename__ = "contribution_versions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    contribution_id: Mapped[str] = mapped_column(ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    proposed_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("contribution_id", "version", name="uq_contribution_version"), Index("ix_contribution_version_contribution", "contribution_id"))


class ContributionReview(Base):
    __tablename__ = "contribution_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    contribution_id: Mapped[str] = mapped_column(ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("action IN ('changes-requested','reviewer-approved','rejected','duplicate','maintainer-approved','github-handoff','merged','published')", name="ck_contribution_review_action"),
        Index("ix_contribution_review_contribution", "contribution_id", "created_at"),
    )


class ReviewComment(Base):
    __tablename__ = "review_comments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    contribution_id: Mapped[str] = mapped_column(ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    body: Mapped[str] = mapped_column(String(4000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_review_comment_contribution", "contribution_id", "created_at"),)


class CommunityReport(Base):
    __tablename__ = "community_reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    reporter_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    entity_id: Mapped[str | None] = mapped_column(String(160), index=True)
    report_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    is_security_report: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolver_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resolution: Mapped[str | None] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (
        CheckConstraint("report_type IN ('incorrect-information','unsafe-content','broken-link','wrong-relationship','duplicate','outdated','copyright-concern','security-concern','other')", name="ck_community_report_type"),
        CheckConstraint("status IN ('open','triaged','investigating','resolved','dismissed','duplicate')", name="ck_community_report_status"),
        Index("ix_community_report_status_created", "status", "created_at"),
    )


class ReputationEvent(Base):
    __tablename__ = "reputation_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_key: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(256), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_reputation_event_user_created", "user_id", "created_at"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    target_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    target_type: Mapped[str] = mapped_column(String(48), nullable=False)
    target_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(2000))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_audit_event_target_created", "target_type", "target_id", "created_at"), Index("ix_audit_event_actor_created", "actor_id", "created_at"))
