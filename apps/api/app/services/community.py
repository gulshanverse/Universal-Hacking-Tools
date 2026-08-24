"""Private proposal/review state over immutable generated knowledge; never a canonical content writer."""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from urllib.parse import urlsplit

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..state.models import (
    AuditEvent, CommunityProfile, CommunityReport, Contribution, ContributionReview,
    ContributionVersion, ReputationEvent, ReviewComment, User, utcnow,
)
from .artifacts import ENTITY_TYPES, artifacts
from .git_provider import GitProvider, HandoffResult, UnavailableGitProvider


CONTRIBUTION_TYPES = {
    "tool", "vulnerability", "concept", "technique", "technology", "defensive-control",
    "lab", "learning-path", "relationship", "source", "verification-correction",
    "content-correction", "broken-link",
}
RESERVED_USERNAMES = {"admin", "administrator", "moderator", "security", "support", "github", "official", "root", "system", "maintainer", "reviewer", "api", "community", "contribute", "profile"}
ROLE_ORDER = {"contributor": 0, "reviewer": 1, "maintainer": 2, "administrator": 3}
EDITABLE = {"draft", "changes-requested"}
WITHDRAWABLE = {"draft", "submitted", "queued", "changes-requested"}
URL_FIELDS = {"official_website", "official_repository", "official_documentation", "source_url", "evidence_url", "website_url", "avatar_url"}
FORBIDDEN_WORDS = {"malware", "credential theft", "credential harvesting", "persistence mechanism", "destructive payload", "unauthorized targeting", "real-world attack automation"}
TYPE_REQUIRED = {
    "tool": {"purpose", "category", "description", "official_website", "official_repository", "official_documentation", "safety_considerations"},
    "vulnerability": {"description", "affected_technology", "impact", "detection", "mitigation", "references", "safety_boundaries"},
    "lab": {"learning_objective", "difficulty", "scope", "fixture_requirements", "evidence_requirements", "assessment_criteria", "safety_model", "reset_behavior", "destroy_behavior"},
    "relationship": {"source_entity", "relationship", "target_entity", "reason"},
    "source": {"source_url", "source_kind", "reason"},
    "verification-correction": {"entity_id", "current_status", "suggested_status", "reason", "evidence_url"},
    "content-correction": {"entity_id", "issue", "proposed_correction"},
    "broken-link": {"entity_id", "source_url", "reason"},
}
TYPE_ALLOWED = {
    "tool": TYPE_REQUIRED["tool"] | {"tags", "platforms", "security_domains"},
    "vulnerability": TYPE_REQUIRED["vulnerability"] | {"name", "severity", "cve", "tags", "security_domains"},
    "lab": TYPE_REQUIRED["lab"] | {"prerequisites", "cleanup"},
    "relationship": TYPE_REQUIRED["relationship"] | {"evidence_url"},
    "source": TYPE_REQUIRED["source"] | {"entity_id"},
    "verification-correction": TYPE_REQUIRED["verification-correction"] | {"verification_method"},
    "content-correction": TYPE_REQUIRED["content-correction"] | {"evidence_url"},
    "broken-link": TYPE_REQUIRED["broken-link"],
    "concept": {"name", "definition", "category", "source_url", "reason"},
    "technique": {"name", "description", "category", "source_url", "reason"},
    "technology": {"name", "description", "category", "source_url", "reason"},
    "defensive-control": {"name", "description", "category", "source_url", "reason"},
    "learning-path": {"name", "description", "source_url", "reason"},
}
REPUTATION = {
    "tool": (10, "approved tool contribution"), "vulnerability": (10, "approved vulnerability contribution"),
    "lab": (15, "approved safe-lab contribution"), "relationship": (3, "accepted relationship correction"),
    "content-correction": (5, "accepted content correction"), "verification-correction": (5, "accepted verification correction"),
}
CONTROLLED_PATHS = {
    "tool": "tools/community-proposals", "vulnerability": "vulnerabilities/community-proposals",
    "concept": "knowledge/concepts/community-proposals", "technique": "knowledge/techniques/community-proposals",
    "technology": "knowledge/technologies/community-proposals", "defensive-control": "knowledge/defensive-controls/community-proposals",
    "lab": "labs/community-proposals", "learning-path": "learning-paths/community-proposals",
    "relationship": "knowledge/community-proposals", "source": "knowledge/community-proposals",
    "verification-correction": "knowledge/community-proposals", "content-correction": "knowledge/community-proposals", "broken-link": "knowledge/community-proposals",
}


def clean_text(value: str, *, field: str, maximum: int) -> str:
    text = value.strip()
    if not text or len(text) > maximum or "\x00" in text or "<" in text or ">" in text:
        raise ValueError(f"{field} must be bounded plain text without markup")
    return text


def normalized_username(value: str) -> str:
    username = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,40}", username) or username in RESERVED_USERNAMES:
        raise ValueError("username is unavailable or invalid")
    return username


def safe_url(value: str | None, *, field: str) -> str | None:
    if value in (None, ""):
        return None
    candidate = value.strip()
    parsed = urlsplit(candidate)
    if len(candidate) > 512 or parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or any(char.isspace() for char in candidate):
        raise ValueError(f"{field} must be a safe HTTPS URL")
    return candidate


def profile_dict(profile: CommunityProfile, *, counts: dict[str, int] | None = None, reputation: int = 0, expertise: list[str] | None = None) -> dict:
    counts = counts or {}
    accepted = sum(counts.values())
    level = "New Contributor" if accepted == 0 else "Trusted Contributor" if accepted >= 10 else "Contributor"
    return {
        "username": profile.username, "display_name": profile.display_name, "bio": profile.bio,
        "avatar_url": profile.avatar_url, "website_url": profile.website_url, "github_username": profile.github_username,
        "joined_at": profile.created_at, "contribution_count": accepted, "contribution_categories": counts,
        "approved_contributions": accepted, "reputation": reputation, "contributor_level": level,
        "expertise_areas": expertise or [], "badges": badges_for(counts),
        "reputation_note": "Reputation reflects accepted contributions and reviewed work; it is not a professional certification.",
    }


def badges_for(counts: dict[str, int]) -> list[str]:
    badges: list[str] = []
    if sum(counts.values()) > 0:
        badges.append("Verified Contributor")
    if counts.get("lab", 0):
        badges.append("Lab Contributor")
    if counts.get("content-correction", 0) or counts.get("verification-correction", 0):
        badges.append("Documentation Contributor")
    return badges


def audit(db: Session, *, actor_id: str | None, target_type: str, target_id: str, action: str, reason: str | None = None, target_user_id: str | None = None, metadata: dict | None = None) -> None:
    db.add(AuditEvent(actor_id=actor_id, target_user_id=target_user_id, target_type=target_type, target_id=target_id, action=action, reason=reason, metadata_json=metadata or {}))


def require_role(user: User, *roles: str) -> None:
    if user.status != "active" or user.role not in roles:
        raise PermissionError("role authorization is required")


def ensure_active(user: User) -> None:
    if user.status != "active":
        raise PermissionError("active contributor status is required")


def create_or_update_profile(db: Session, user: User, payload: dict, *, create: bool = False) -> CommunityProfile:
    ensure_active(user)
    profile = db.get(CommunityProfile, user.id)
    if create:
        if profile:
            raise ValueError("community profile already exists")
        username = normalized_username(payload["username"])
        if db.scalar(select(CommunityProfile).where(CommunityProfile.username == username)):
            raise ValueError("username is unavailable or invalid")
        profile = CommunityProfile(user_id=user.id, username=username)
        db.add(profile)
    elif not profile:
        raise ValueError("create a community profile before updating it")
    for key, maximum in (("display_name", 80), ("bio", 1000)):
        if key in payload and payload[key] is not None:
            setattr(profile, key, clean_text(payload[key], field=key.replace("_", " "), maximum=maximum))
    for key in ("avatar_url", "website_url"):
        if key in payload:
            setattr(profile, key, safe_url(payload[key], field=key.replace("_", " ")))
    if "github_username" in payload and payload["github_username"] is not None:
        profile.github_username = payload["github_username"].strip()
    if "is_public" in payload and payload["is_public"] is not None:
        profile.is_public = bool(payload["is_public"])
    audit(db, actor_id=user.id, target_type="community-profile", target_id=user.id, action="created" if create else "updated")
    return profile


def proposal_validation(contribution_type: str, title: str, description: str, proposed_data: dict) -> tuple[dict, list[dict], dict]:
    if contribution_type not in CONTRIBUTION_TYPES:
        raise ValueError("unsupported contribution type")
    clean_title = clean_text(title, field="title", maximum=180)
    clean_description = clean_text(description, field="description", maximum=8000)
    if not isinstance(proposed_data, dict):
        raise ValueError("proposed data must be an object")
    raw = json.dumps(proposed_data, sort_keys=True)
    if len(raw) > 32768:
        raise ValueError("proposed content must be 32 KiB or smaller")
    missing = sorted(TYPE_REQUIRED.get(contribution_type, set()) - {key for key, value in proposed_data.items() if value not in (None, "", [], {})})
    errors: list[str] = []
    warnings: list[str] = []
    unexpected = sorted(set(proposed_data) - TYPE_ALLOWED[contribution_type])
    if unexpected:
        errors.append("proposal contains fields outside the controlled template: " + ", ".join(unexpected))
    haystack = f"{clean_title}\n{clean_description}\n{raw}".casefold()
    unsafe = sorted(word for word in FORBIDDEN_WORDS if word in haystack)
    if unsafe:
        errors.append("proposal contains prohibited unsafe-contribution language")
    for key, value in proposed_data.items():
        if key in URL_FIELDS and value not in (None, ""):
            try:
                safe_url(str(value), field=key)
            except ValueError as exc:
                errors.append(str(exc))
        if key == "references" and value not in (None, ""):
            if not isinstance(value, list) or len(value) > 12:
                errors.append("references must be a list of at most 12 safe HTTPS URLs")
            else:
                for url in value:
                    try:
                        safe_url(str(url), field="reference")
                    except ValueError as exc:
                        errors.append(str(exc))
    if contribution_type == "relationship":
        source, target = proposed_data.get("source_entity"), proposed_data.get("target_entity")
        relationship = proposed_data.get("relationship")
        if source and not artifacts.resolve(str(source)):
            errors.append("relationship source entity is not in generated knowledge")
        if target and not artifacts.resolve(str(target)):
            errors.append("relationship target entity is not in generated knowledge")
        if relationship and relationship not in artifacts.engine("graph").relationship_types():
            errors.append("relationship type is not in the generated vocabulary")
    if contribution_type == "lab":
        safety = str(proposed_data.get("safety_model", "")).casefold()
        required_safety = ("local", "synthetic", "no public network", "finite", "ephemeral")
        absent = [item for item in required_safety if item not in safety]
        if absent:
            errors.append("executable or safe-lab proposals must state local-only, synthetic, no-public-network, finite, and ephemeral controls")
    if missing:
        warnings.append("missing required proposal fields: " + ", ".join(missing))
    quality = max(0, 100 - len(missing) * 10 - len(errors) * 30)
    duplicate_candidates = duplicate_candidates_for(contribution_type, clean_title, proposed_data)
    impact = proposal_impact(contribution_type, proposed_data)
    return ({"valid": not errors, "quality_score": quality, "missing_fields": missing, "errors": errors, "warnings": warnings, "safety_checked": True, "canonical_knowledge_unchanged": True}, duplicate_candidates, impact)


def duplicate_candidates_for(contribution_type: str, title: str, proposed_data: dict) -> list[dict]:
    entity_type = contribution_type if contribution_type in ENTITY_TYPES else None
    normalized = re.sub(r"[^a-z0-9]+", "", title.casefold())
    candidates = []
    for document in artifacts.documents():
        if entity_type and document.get("type") != entity_type:
            continue
        name = str(document.get("name", ""))
        if normalized and normalized == re.sub(r"[^a-z0-9]+", "", name.casefold()):
            candidates.append({"entity_id": document["id"], "entity_type": document["type"], "name": name, "reason": "normalized name matches generated knowledge"})
    return candidates[:10]


def proposal_impact(contribution_type: str, proposed_data: dict) -> dict:
    if contribution_type != "relationship":
        return {"available": False, "reason": "Impact preview is available for generated-entity relationship proposals only."}
    source = proposed_data.get("source_entity")
    target = proposed_data.get("target_entity")
    if not source or not target or not artifacts.resolve(str(source)) or not artifacts.resolve(str(target)):
        return {"available": False, "reason": "Select two existing generated entities to calculate impact."}
    graph = artifacts.engine("graph")
    source_impact, target_impact = graph.impact(str(source), depth=2, node_limit=100), graph.impact(str(target), depth=2, node_limit=100)
    return {
        "available": True, "simulation_only": True, "proposed_edge": {"source": str(source), "target": str(target), "relationship": proposed_data.get("relationship")},
        "source_affected": {key: len(value) for key, value in source_impact["affected"].items()},
        "target_affected": {key: len(value) for key, value in target_impact["affected"].items()},
        "graph_version": graph.graph_version,
        "reason": "Current generated graph impact only; proposed edges are never inserted into canonical graph artifacts.",
    }


def create_contribution(db: Session, user: User, *, contribution_type: str, title: str, description: str, proposed_data: dict) -> Contribution:
    ensure_active(user)
    validation, duplicates, impact = proposal_validation(contribution_type, title, description, proposed_data)
    row = Contribution(user_id=user.id, contribution_type=contribution_type, title=clean_text(title, field="title", maximum=180), description=clean_text(description, field="description", maximum=8000), proposed_data=proposed_data, validation=validation, duplicate_candidates=duplicates, impact=impact, knowledge_version_before=artifacts.version(), reviewer_recommendations=[])
    db.add(row); db.flush()
    row.reviewer_recommendations = reviewer_recommendations(db, row)
    db.add(ContributionVersion(contribution_id=row.id, version=1, summary="Initial private proposal draft.", proposed_data=proposed_data, description=row.description))
    audit(db, actor_id=user.id, target_type="contribution", target_id=row.id, action="draft-created", metadata={"type": contribution_type})
    return row


def update_contribution(db: Session, user: User, row: Contribution, payload: dict) -> Contribution:
    ensure_active(user)
    if row.user_id != user.id:
        raise LookupError("contribution not found")
    if row.status not in EDITABLE:
        raise ValueError("contribution is immutable in its current state")
    title = payload.get("title", row.title)
    description = payload.get("description", row.description)
    proposed_data = payload.get("proposed_data", row.proposed_data)
    validation, duplicates, impact = proposal_validation(row.contribution_type, title, description, proposed_data)
    row.title, row.description, row.proposed_data = clean_text(title, field="title", maximum=180), clean_text(description, field="description", maximum=8000), proposed_data
    row.validation, row.duplicate_candidates, row.impact = validation, duplicates, impact
    version = (db.scalar(select(func.max(ContributionVersion.version)).where(ContributionVersion.contribution_id == row.id)) or 0) + 1
    db.add(ContributionVersion(contribution_id=row.id, version=version, summary=clean_text(payload["summary"], field="revision summary", maximum=500), proposed_data=proposed_data, description=row.description))
    audit(db, actor_id=user.id, target_type="contribution", target_id=row.id, action="draft-revised", metadata={"version": version})
    return row


def submit_contribution(db: Session, user: User, row: Contribution) -> Contribution:
    ensure_active(user)
    if row.user_id != user.id:
        raise LookupError("contribution not found")
    if row.status not in EDITABLE | {"validation-failed"}:
        raise ValueError("contribution cannot be submitted in its current state")
    validation, duplicates, impact = proposal_validation(row.contribution_type, row.title, row.description, row.proposed_data)
    row.validation, row.duplicate_candidates, row.impact = validation, duplicates, impact
    row.status = "queued" if validation["valid"] else "validation-failed"
    row.submitted_at = utcnow()
    audit(db, actor_id=user.id, target_type="contribution", target_id=row.id, action="submitted" if validation["valid"] else "validation-failed", metadata={"quality_score": validation["quality_score"]})
    return row


def withdraw_contribution(db: Session, user: User, row: Contribution) -> Contribution:
    ensure_active(user)
    if row.user_id != user.id:
        raise LookupError("contribution not found")
    if row.status not in WITHDRAWABLE:
        raise ValueError("contribution cannot be withdrawn in its current state")
    row.status = "withdrawn"; audit(db, actor_id=user.id, target_type="contribution", target_id=row.id, action="withdrawn")
    return row


def reviewer_action(db: Session, actor: User, row: Contribution, action: str, reason: str) -> Contribution:
    require_role(actor, "reviewer", "maintainer", "administrator")
    reason = clean_text(reason, field="review reason", maximum=2000)
    if row.user_id == actor.id:
        raise PermissionError("reviewers cannot review their own contribution")
    allowed = {
        "changes-requested": ({"queued", "under-review"}, "changes-requested"),
        "reviewer-approved": ({"queued", "under-review", "changes-requested"}, "under-review"),
        "rejected": ({"queued", "under-review", "changes-requested"}, "rejected"),
        "duplicate": ({"queued", "under-review", "changes-requested"}, "rejected"),
    }
    if action not in allowed:
        raise PermissionError("review action requires maintainer authorization")
    source, destination = allowed[action]
    if row.status not in source:
        raise ValueError("invalid contribution lifecycle transition")
    row.status, row.reviewed_at = destination, utcnow()
    db.add(ContributionReview(contribution_id=row.id, reviewer_id=actor.id, action=action, reason=reason))
    audit(db, actor_id=actor.id, target_type="contribution", target_id=row.id, action=action, reason=reason)
    return row


def maintainer_action(db: Session, actor: User, row: Contribution, action: str, reason: str) -> Contribution:
    require_role(actor, "maintainer", "administrator")
    reason = clean_text(reason, field="maintainer reason", maximum=2000)
    if row.user_id == actor.id and action in {"maintainer-approved", "merged", "published"}:
        raise PermissionError("maintainers cannot finalize their own contribution")
    transitions = {
        "maintainer-approved": ({"under-review", "queued"}, "approved"),
        "rejected": ({"queued", "under-review", "changes-requested", "approved"}, "rejected"),
        "merged": ({"approved"}, "merged"),
        "published": ({"merged"}, "published"),
    }
    if action not in transitions:
        raise ValueError("invalid maintainer action")
    source, destination = transitions[action]
    if row.status not in source:
        raise ValueError("invalid contribution lifecycle transition")
    if action == "merged" and row.github_handoff_status != "created":
        raise ValueError("a confirmed Git provider pull request is required before merge state")
    row.status, row.reviewed_at = destination, utcnow()
    if destination == "merged": row.merged_at = utcnow()
    if destination == "published":
        row.published_at = utcnow(); row.knowledge_version_after = artifacts.version(); award_reputation(db, row)
    db.add(ContributionReview(contribution_id=row.id, reviewer_id=actor.id, action=action, reason=reason))
    audit(db, actor_id=actor.id, target_type="contribution", target_id=row.id, action=action, reason=reason)
    return row


def add_comment(db: Session, actor: User, row: Contribution, body: str) -> ReviewComment:
    require_role(actor, "reviewer", "maintainer", "administrator")
    if row.user_id == actor.id:
        raise PermissionError("reviewers cannot comment on their own contribution")
    comment = ReviewComment(contribution_id=row.id, author_id=actor.id, body=clean_text(body, field="comment", maximum=4000))
    db.add(comment); db.flush(); audit(db, actor_id=actor.id, target_type="contribution", target_id=row.id, action="review-comment", metadata={"comment_id": comment.id})
    return comment


def award_reputation(db: Session, row: Contribution) -> None:
    if not row.user_id:
        return
    points, reason = REPUTATION.get(row.contribution_type, (5, "approved community contribution"))
    key = f"published:{row.id}"
    if db.scalar(select(ReputationEvent).where(ReputationEvent.event_key == key)):
        return
    db.add(ReputationEvent(user_id=row.user_id, event_key=key, reason=reason, points=points, source_type="contribution", source_id=row.id))


def reputation_summary(db: Session, user_id: str) -> dict:
    events = db.scalars(select(ReputationEvent).where(ReputationEvent.user_id == user_id).order_by(ReputationEvent.created_at)).all()
    return {"total": sum(item.points for item in events), "events": [{"reason": item.reason, "points": item.points, "source_type": item.source_type, "source_id": item.source_id, "created_at": item.created_at} for item in events]}


def contribution_counts(db: Session, user_id: str, *, public_only: bool = False) -> dict[str, int]:
    statement = select(Contribution.contribution_type, func.count()).where(Contribution.user_id == user_id)
    if public_only:
        statement = statement.where(Contribution.status == "published")
    return {kind: count for kind, count in db.execute(statement.group_by(Contribution.contribution_type)).all()}


def reviewer_recommendations(db: Session, row: Contribution) -> list[dict]:
    """Explainable workload-aware suggestions; only maintainers may assign."""
    candidates = db.scalars(select(User).where(User.status == "active", User.role.in_(("reviewer", "maintainer", "administrator")), User.id != row.user_id)).all()
    suggestions = []
    for candidate in candidates:
        expertise = contribution_counts(db, candidate.id, public_only=True).get(row.contribution_type, 0)
        workload = db.scalar(select(func.count()).select_from(Contribution).where(Contribution.assigned_reviewer_id == candidate.id, Contribution.status.in_(("queued", "under-review", "changes-requested")))) or 0
        score = expertise * 10 - workload * 2
        suggestions.append({"reviewer_id": candidate.id, "role": candidate.role, "expertise_matches": expertise, "open_workload": workload, "score": score, "reason": "Recommendation combines approved contribution type experience, open assigned-review workload, and author-conflict exclusion."})
    return sorted(suggestions, key=lambda item: (-item["score"], item["open_workload"], item["reviewer_id"]))[:10]


def assign_reviewer(db: Session, actor: User, row: Contribution, reviewer_id: str, reason: str) -> Contribution:
    require_role(actor, "maintainer", "administrator")
    reviewer = db.get(User, reviewer_id)
    if not reviewer or reviewer.status != "active" or reviewer.role not in {"reviewer", "maintainer", "administrator"} or reviewer.id == row.user_id:
        raise ValueError("reviewer is not eligible for assignment")
    if row.status not in {"queued", "under-review", "changes-requested"}:
        raise ValueError("reviewer assignment is unavailable in the current lifecycle state")
    row.assigned_reviewer_id = reviewer.id
    row.reviewer_recommendations = reviewer_recommendations(db, row)
    audit(db, actor_id=actor.id, target_type="contribution", target_id=row.id, action="reviewer-assigned", reason=clean_text(reason, field="assignment reason", maximum=2000), target_user_id=reviewer.id)
    return row


def expertise_for(db: Session, user_id: str) -> list[str]:
    rows = db.scalars(select(Contribution).where(Contribution.user_id == user_id, Contribution.status == "published")).all()
    areas = Counter()
    for row in rows:
        for value in row.proposed_data.get("security_domains", []) if isinstance(row.proposed_data.get("security_domains", []), list) else []:
            areas[str(value)] += 1
        category = row.proposed_data.get("category")
        if category:
            areas[str(category)] += 1
    return [name for name, _ in sorted(areas.items(), key=lambda item: (-item[1], item[0]))[:6]]


def public_profile(db: Session, username: str) -> dict | None:
    profile = db.scalar(select(CommunityProfile).where(CommunityProfile.username == normalized_username(username), CommunityProfile.is_public.is_(True), CommunityProfile.is_hidden.is_(False)))
    if not profile:
        return None
    counts = contribution_counts(db, profile.user_id, public_only=True)
    return profile_dict(profile, counts=counts, reputation=reputation_summary(db, profile.user_id)["total"], expertise=expertise_for(db, profile.user_id))


def contribution_view(db: Session, row: Contribution, *, include_private: bool = False) -> dict:
    profile = db.get(CommunityProfile, row.user_id) if row.user_id else None
    public_author = profile.username if profile and profile.is_public and not profile.is_hidden else "Former Contributor" if not row.user_id else None
    result = {"id": row.id, "type": row.contribution_type, "title": row.title, "description": row.description, "status": row.status, "created_at": row.created_at, "updated_at": row.updated_at, "submitted_at": row.submitted_at, "reviewed_at": row.reviewed_at, "merged_at": row.merged_at, "published_at": row.published_at, "author": public_author, "github_pr_url": row.github_pr_url if row.status in {"merged", "published"} else None, "knowledge_version_before": row.knowledge_version_before, "knowledge_version_after": row.knowledge_version_after}
    if include_private:
        versions = db.scalars(select(ContributionVersion).where(ContributionVersion.contribution_id == row.id).order_by(ContributionVersion.version)).all()
        reviews = db.scalars(select(ContributionReview).where(ContributionReview.contribution_id == row.id).order_by(ContributionReview.created_at)).all()
        comments = db.scalars(select(ReviewComment).where(ReviewComment.contribution_id == row.id).order_by(ReviewComment.created_at)).all()
        result.update({"proposed_content_label": "PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE", "proposed_data": row.proposed_data, "validation": row.validation, "duplicate_candidates": row.duplicate_candidates, "impact": row.impact, "github_handoff_status": row.github_handoff_status, "assigned_reviewer_id": row.assigned_reviewer_id, "reviewer_recommendations": row.reviewer_recommendations, "versions": [{"version": item.version, "summary": item.summary, "description": item.description, "proposed_data": item.proposed_data, "created_at": item.created_at} for item in versions], "reviews": [{"action": item.action, "reason": item.reason, "created_at": item.created_at} for item in reviews], "comments": [{"body": item.body, "created_at": item.created_at} for item in comments]})
    return result


def create_report(db: Session, user: User, *, report_type: str, entity_id: str | None, description: str) -> CommunityReport:
    ensure_active(user)
    if entity_id and not artifacts.resolve(entity_id):
        raise ValueError("report entity is not in generated knowledge")
    security = report_type == "security-concern"
    row = CommunityReport(reporter_id=user.id, entity_id=entity_id, report_type=report_type, description=clean_text(description, field="report description", maximum=4000), is_security_report=security)
    db.add(row); db.flush(); audit(db, actor_id=user.id, target_type="community-report", target_id=row.id, action="created", metadata={"security_report": security})
    return row


def resolve_report(db: Session, actor: User, row: CommunityReport, *, status: str, resolution: str) -> CommunityReport:
    require_role(actor, "maintainer", "administrator")
    row.status, row.resolver_id, row.resolution, row.resolved_at = status, actor.id, clean_text(resolution, field="report resolution", maximum=2000), utcnow()
    audit(db, actor_id=actor.id, target_type="community-report", target_id=row.id, action=f"report-{status}", reason=row.resolution)
    return row


def moderate_user(db: Session, actor: User, target: User, *, status: str, reason: str) -> User:
    require_role(actor, "administrator")
    if target.id == actor.id:
        raise PermissionError("administrators cannot moderate their own account")
    target.status = status
    target.suspended_at = utcnow() if status == "suspended" else None
    audit(db, actor_id=actor.id, target_user_id=target.id, target_type="user", target_id=target.id, action=f"user-{status}", reason=clean_text(reason, field="moderation reason", maximum=2000))
    return target


def assign_role(db: Session, actor: User, target: User, *, role: str, reason: str) -> User:
    require_role(actor, "administrator")
    if role not in ROLE_ORDER or target.id == actor.id:
        raise PermissionError("role assignment is not allowed")
    target.role = role
    audit(db, actor_id=actor.id, target_user_id=target.id, target_type="user", target_id=target.id, action="role-assigned", reason=clean_text(reason, field="role assignment reason", maximum=2000), metadata={"role": role})
    return target


def controlled_handoff_files(row: Contribution) -> list[dict[str, str]]:
    base = CONTROLLED_PATHS[row.contribution_type]
    path = f"{base}/{row.id}.md"
    body = "# Proposed Community Contribution\n\n> PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE\n\n" + row.description + "\n\n```json\n" + json.dumps(row.proposed_data, indent=2, sort_keys=True) + "\n```\n"
    return [{"path": path, "content": body}]


def handoff_to_git(db: Session, actor: User, row: Contribution, provider: GitProvider | None = None) -> HandoffResult:
    require_role(actor, "maintainer", "administrator")
    if row.status != "approved":
        raise ValueError("only approved contributions can enter Git handoff")
    result = (provider or UnavailableGitProvider()).create_pull_request(contribution_id=row.id, branch=f"community/{row.contribution_type}-{row.id}", files=controlled_handoff_files(row), title=f"community: {row.title}", body="Validated proposal awaiting repository CI and human review.")
    row.github_handoff_status = result.status
    if result.status == "created":
        row.github_pr_url, row.github_commit_sha = result.pull_request_url, result.commit_sha
    db.add(ContributionReview(contribution_id=row.id, reviewer_id=actor.id, action="github-handoff", reason=result.message))
    audit(db, actor_id=actor.id, target_type="contribution", target_id=row.id, action="github-handoff", reason=result.message, metadata={"status": result.status})
    return result


def opportunities() -> dict:
    review = artifacts.json("review-queue.json")
    health = artifacts.json("knowledge-health.json")
    graph = artifacts.json("graph-health.json")
    completeness = artifacts.json("content-completeness.json")
    items = []
    for entry in review.get("items", [])[:25]:
        items.append({"kind": "needs-review", "entity_id": entry.get("id"), "entity_type": entry.get("type"), "title": entry.get("name") or entry.get("id"), "priority": entry.get("priority", "normal"), "reason": entry.get("reason", "Generated review queue item.")})
    return {"knowledge_version": artifacts.version(), "generated_at": artifacts.generated_at(), "summary": {"needs_review": len(review.get("items", [])), "orphans": int(graph.get("orphan_count", 0)), "missing_sources": int(health.get("missing_sources", 0)), "incomplete_entities": len([item for item in completeness.get("items", []) if item.get("score", 100) < 100])}, "items": items, "boundary": "Generated opportunities are read-only reviewer assistance; proposals never change canonical knowledge directly."}


def public_metrics(db: Session) -> dict:
    total_contributors = db.scalar(select(func.count()).select_from(CommunityProfile).where(CommunityProfile.is_public.is_(True), CommunityProfile.is_hidden.is_(False))) or 0
    approved = db.scalar(select(func.count()).select_from(Contribution).where(Contribution.status.in_(("merged", "published")))) or 0
    open_proposals = db.scalar(select(func.count()).select_from(Contribution).where(Contribution.status.in_(("queued", "under-review", "changes-requested")))) or 0
    return {"total_contributors": total_contributors, "approved_contributions": approved, "open_proposals": open_proposals, "review_backlog": open_proposals}
