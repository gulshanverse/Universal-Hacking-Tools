"""phase 10 community collaboration application-state schema

Revision ID: 20260824_02
Revises: 20260823_01
Create Date: 2026-08-24
"""
from alembic import op
import sqlalchemy as sa


revision = "20260824_02"
down_revision = "20260823_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("role", sa.String(32), nullable=False, server_default="contributor"))
        batch.add_column(sa.Column("suspended_at", sa.DateTime(timezone=True)))
        batch.create_check_constraint("ck_users_role", "role IN ('contributor','reviewer','maintainer','administrator')")

    op.create_table(
        "community_profiles",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("username", sa.String(40), nullable=False, unique=True),
        sa.Column("display_name", sa.String(80)), sa.Column("bio", sa.String(1000)),
        sa.Column("avatar_url", sa.String(512)), sa.Column("website_url", sa.String(512)), sa.Column("github_username", sa.String(39)),
        sa.Column("is_public", sa.Boolean(), nullable=False), sa.Column("is_hidden", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(username) >= 3 AND length(username) <= 40", name="ck_community_username_length"),
        sa.CheckConstraint("username = lower(username)", name="ck_community_username_normalized"),
    )

    op.create_table(
        "contributions",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("contribution_type", sa.String(48), nullable=False), sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False), sa.Column("proposed_data", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("validation", sa.JSON(), nullable=False),
        sa.Column("duplicate_candidates", sa.JSON(), nullable=False), sa.Column("impact", sa.JSON(), nullable=False),
        sa.Column("assigned_reviewer_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("reviewer_recommendations", sa.JSON(), nullable=False),
        sa.Column("github_issue_url", sa.String(512)), sa.Column("github_pr_url", sa.String(512)), sa.Column("github_commit_sha", sa.String(64)),
        sa.Column("github_handoff_status", sa.String(24)), sa.Column("knowledge_version_before", sa.String(128)), sa.Column("knowledge_version_after", sa.String(128)),
        sa.Column("submitted_at", sa.DateTime(timezone=True)), sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("merged_at", sa.DateTime(timezone=True)), sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("contribution_type IN ('tool','vulnerability','concept','technique','technology','defensive-control','lab','learning-path','relationship','source','verification-correction','content-correction','broken-link')", name="ck_contribution_type"),
        sa.CheckConstraint("status IN ('draft','submitted','validation-failed','queued','under-review','changes-requested','approved','rejected','withdrawn','merged','published')", name="ck_contribution_status"),
        sa.CheckConstraint("github_handoff_status IS NULL OR github_handoff_status IN ('queued','failed','created')", name="ck_contribution_handoff_status"),
    )
    op.create_index("ix_contributions_user_id", "contributions", ["user_id"])
    op.create_index("ix_contribution_status_created", "contributions", ["status", "created_at"])
    op.create_index("ix_contribution_type_created", "contributions", ["contribution_type", "created_at"])
    op.create_index("ix_contribution_assigned_reviewer", "contributions", ["assigned_reviewer_id", "status"])

    op.create_table(
        "contribution_versions",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("contribution_id", sa.String(36), sa.ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False), sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("proposed_data", sa.JSON(), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("contribution_id", "version", name="uq_contribution_version"),
    )
    op.create_index("ix_contribution_version_contribution", "contribution_versions", ["contribution_id"])

    op.create_table(
        "contribution_reviews",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("contribution_id", sa.String(36), sa.ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("action", sa.String(32), nullable=False),
        sa.Column("reason", sa.String(2000), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("action IN ('changes-requested','reviewer-approved','rejected','duplicate','maintainer-approved','github-handoff','merged','published')", name="ck_contribution_review_action"),
    )
    op.create_index("ix_contribution_review_contribution", "contribution_reviews", ["contribution_id", "created_at"])

    op.create_table(
        "review_comments",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("contribution_id", sa.String(36), sa.ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("body", sa.String(4000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_review_comment_contribution", "review_comments", ["contribution_id", "created_at"])

    op.create_table(
        "community_reports",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("reporter_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("entity_id", sa.String(160)), sa.Column("report_type", sa.String(32), nullable=False), sa.Column("description", sa.String(4000), nullable=False),
        sa.Column("status", sa.String(32), nullable=False), sa.Column("is_security_report", sa.Boolean(), nullable=False),
        sa.Column("resolver_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("resolution", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("report_type IN ('incorrect-information','unsafe-content','broken-link','wrong-relationship','duplicate','outdated','copyright-concern','security-concern','other')", name="ck_community_report_type"),
        sa.CheckConstraint("status IN ('open','triaged','investigating','resolved','dismissed','duplicate')", name="ck_community_report_status"),
    )
    op.create_index("ix_community_reports_reporter_id", "community_reports", ["reporter_id"])
    op.create_index("ix_community_reports_entity_id", "community_reports", ["entity_id"])
    op.create_index("ix_community_report_status_created", "community_reports", ["status", "created_at"])

    op.create_table(
        "reputation_events",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("event_key", sa.String(160), nullable=False, unique=True), sa.Column("reason", sa.String(256), nullable=False), sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False), sa.Column("source_id", sa.String(64), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_reputation_event_user_created", "reputation_events", ["user_id", "created_at"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("target_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("target_type", sa.String(48), nullable=False),
        sa.Column("target_id", sa.String(64), nullable=False), sa.Column("action", sa.String(64), nullable=False), sa.Column("reason", sa.String(2000)),
        sa.Column("metadata_json", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_event_target_created", "audit_events", ["target_type", "target_id", "created_at"])
    op.create_index("ix_audit_event_actor_created", "audit_events", ["actor_id", "created_at"])


def downgrade() -> None:
    for index, table in (
        ("ix_audit_event_actor_created", "audit_events"), ("ix_audit_event_target_created", "audit_events"),
        ("ix_reputation_event_user_created", "reputation_events"), ("ix_community_report_status_created", "community_reports"),
        ("ix_community_reports_entity_id", "community_reports"), ("ix_community_reports_reporter_id", "community_reports"),
        ("ix_review_comment_contribution", "review_comments"), ("ix_contribution_review_contribution", "contribution_reviews"),
        ("ix_contribution_version_contribution", "contribution_versions"), ("ix_contribution_assigned_reviewer", "contributions"), ("ix_contribution_type_created", "contributions"),
        ("ix_contribution_status_created", "contributions"), ("ix_contributions_user_id", "contributions"),
    ):
        op.drop_index(index, table_name=table)
    for table in ("audit_events", "reputation_events", "community_reports", "review_comments", "contribution_reviews", "contribution_versions", "contributions", "community_profiles"):
        op.drop_table(table)
    with op.batch_alter_table("users") as batch:
        batch.drop_constraint("ck_users_role", type_="check")
        batch.drop_column("suspended_at")
        batch.drop_column("role")
