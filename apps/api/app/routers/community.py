"""Phase 10 collaboration routes. All content is proposal state, never canonical knowledge mutation."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.contracts import (
    CommunityProfileCreate, CommunityProfilePatch, CommunityReportCreate, ContributionCreate,
    ContributionPatch, ContributionSubmit, GithubHandoffRequest, ReportResolution,
    ReviewActionRequest, ReviewCommentCreate, ReviewerAssignmentRequest, RoleAssignmentRequest, UserModerationRequest,
)
from ..services.community import (
    add_comment, assign_role, contribution_counts, contribution_view, create_contribution,
    create_or_update_profile, create_report, handoff_to_git, maintainer_action, moderate_user,
    opportunities, public_metrics, public_profile, reputation_summary, require_role,
    assign_reviewer,
    resolve_report, reviewer_action, submit_contribution, update_contribution, withdraw_contribution,
)
from ..services.rate_limit import LocalRateLimiter
from ..state.auth import Principal, csrf_protected, current_principal
from ..state.database import get_db
from ..state.models import CommunityProfile, CommunityReport, Contribution, User


router = APIRouter(tags=["community", "collaboration"])
submission_limiter = LocalRateLimiter(limit=10, window_seconds=3600)
report_limiter = LocalRateLimiter(limit=20, window_seconds=3600)
profile_limiter = LocalRateLimiter(limit=12, window_seconds=3600)
review_limiter = LocalRateLimiter(limit=60, window_seconds=3600)


def rejected(exc: Exception) -> None:
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, PermissionError):
        raise HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, LookupError):
        raise HTTPException(status_code=404, detail="resource not found")
    raise HTTPException(status_code=422, detail=str(exc))


def owned_contribution(db: Session, user_id: str, contribution_id: str) -> Contribution:
    row = db.scalar(select(Contribution).where(Contribution.id == contribution_id, Contribution.user_id == user_id))
    if not row:
        raise HTTPException(status_code=404, detail="contribution not found")
    return row


def reviewer_contribution(db: Session, contribution_id: str) -> Contribution:
    row = db.get(Contribution, contribution_id)
    if not row:
        raise HTTPException(status_code=404, detail="contribution not found")
    return row


@router.get("/community/profile/{username}", summary="Read one opt-in public contributor profile")
def get_public_profile(username: str, db: Session = Depends(get_db)):
    try:
        row = public_profile(db, username)
    except ValueError:
        row = None
    if not row:
        raise HTTPException(status_code=404, detail="public contributor profile not found")
    return row


@router.get("/community/contributors", summary="List public contributor profiles")
def contributors(q: str | None = Query(default=None, max_length=40), limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0, le=10000), db: Session = Depends(get_db)):
    statement = select(CommunityProfile).where(CommunityProfile.is_public.is_(True), CommunityProfile.is_hidden.is_(False)).order_by(CommunityProfile.username)
    if q:
        statement = statement.where(CommunityProfile.username.contains(q.strip().lower()))
    rows = db.scalars(statement).all()
    items = []
    for row in rows[offset:offset + limit]:
        profile = public_profile(db, row.username)
        if profile:
            items.append(profile)
    return {"items": items, "total": len(rows), "limit": limit, "offset": offset}


@router.get("/community/contributions", summary="List published community contributions only")
def published_contributions(contribution_type: str | None = Query(default=None), limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0, le=10000), db: Session = Depends(get_db)):
    statement = select(Contribution).where(Contribution.status == "published").order_by(Contribution.published_at.desc(), Contribution.id)
    if contribution_type:
        statement = statement.where(Contribution.contribution_type == contribution_type)
    rows = db.scalars(statement).all()
    return {"items": [contribution_view(db, row) for row in rows[offset:offset + limit]], "total": len(rows), "limit": limit, "offset": offset}


@router.get("/community/contributions/{contribution_id}", summary="Read one published community contribution")
def published_contribution(contribution_id: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Contribution).where(Contribution.id == contribution_id, Contribution.status == "published"))
    if not row:
        raise HTTPException(status_code=404, detail="published contribution not found")
    return contribution_view(db, row)


@router.get("/community/opportunities", summary="Read current generated contribution opportunities")
def community_opportunities():
    return opportunities()


@router.get("/community/metrics", summary="Read aggregate public community health metrics")
def community_metrics(db: Session = Depends(get_db)):
    return public_metrics(db)


@router.get("/community/reputation/{username}", summary="Read public aggregate reputation for an opt-in contributor")
def public_reputation(username: str, db: Session = Depends(get_db)):
    profile = db.scalar(select(CommunityProfile).where(CommunityProfile.username == username.strip().lower(), CommunityProfile.is_public.is_(True), CommunityProfile.is_hidden.is_(False)))
    if not profile:
        raise HTTPException(status_code=404, detail="public contributor profile not found")
    total = reputation_summary(db, profile.user_id)["total"]
    return {"username": profile.username, "reputation": total, "note": "Reputation is based on accepted contributions and reviewed work; it grants no role or certification."}


@router.get("/me/community/profile", summary="Read the authenticated contributor profile")
def my_profile(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    row = db.get(CommunityProfile, principal.user.id)
    return {"profile": None if not row else {"username": row.username, "display_name": row.display_name, "bio": row.bio, "avatar_url": row.avatar_url, "website_url": row.website_url, "github_username": row.github_username, "is_public": row.is_public, "is_hidden": row.is_hidden, "created_at": row.created_at}, "role": principal.user.role, "status": principal.user.status}


@router.post("/me/community/profile", summary="Create the authenticated contributor profile")
def create_profile(payload: CommunityProfileCreate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    profile_limiter.check(f"community-profile:{principal.user.id}")
    try:
        row = create_or_update_profile(db, principal.user, payload.model_dump(), create=True); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"username": row.username, "is_public": row.is_public, "created_at": row.created_at}


@router.patch("/me/community/profile", summary="Update safe contributor profile fields")
def patch_profile(payload: CommunityProfilePatch, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    profile_limiter.check(f"community-profile:{principal.user.id}")
    try:
        row = create_or_update_profile(db, principal.user, payload.model_dump(exclude_unset=True), create=False); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"username": row.username, "is_public": row.is_public, "updated_at": row.updated_at}


@router.get("/me/contributions", summary="List only the authenticated contributor's proposal history")
def my_contributions(limit: int = Query(default=30, ge=1, le=100), offset: int = Query(default=0, ge=0, le=10000), principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    rows = db.scalars(select(Contribution).where(Contribution.user_id == principal.user.id).order_by(Contribution.created_at.desc())).all()
    return {"items": [contribution_view(db, row, include_private=True) for row in rows[offset:offset + limit]], "total": len(rows), "limit": limit, "offset": offset}


@router.post("/me/contributions", summary="Create a private proposed contribution")
def create_my_contribution(payload: ContributionCreate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    submission_limiter.check(f"community-contribution:{principal.user.id}")
    try:
        row = create_contribution(db, principal.user, **payload.model_dump()); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.get("/me/contributions/{contribution_id}", summary="Read one owner-scoped proposed contribution")
def my_contribution(contribution_id: str, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return contribution_view(db, owned_contribution(db, principal.user.id, contribution_id), include_private=True)


@router.patch("/me/contributions/{contribution_id}", summary="Revise one editable contributor proposal")
def patch_my_contribution(contribution_id: str, payload: ContributionPatch, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        row = update_contribution(db, principal.user, owned_contribution(db, principal.user.id, contribution_id), payload.model_dump(exclude_none=True)); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.post("/me/contributions/{contribution_id}/submit", summary="Run deterministic validation and submit an owned proposal")
def submit_my_contribution(contribution_id: str, payload: ContributionSubmit, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    if not payload.confirmation:
        raise HTTPException(status_code=422, detail="submission confirmation is required")
    try:
        row = submit_contribution(db, principal.user, owned_contribution(db, principal.user.id, contribution_id)); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.post("/me/contributions/{contribution_id}/withdraw", summary="Withdraw an editable owned proposal")
def withdraw_my_contribution(contribution_id: str, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        row = withdraw_contribution(db, principal.user, owned_contribution(db, principal.user.id, contribution_id)); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.get("/me/reports", summary="List only reports filed by the authenticated user")
def my_reports(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    rows = db.scalars(select(CommunityReport).where(CommunityReport.reporter_id == principal.user.id).order_by(CommunityReport.created_at.desc())).all()
    return {"items": [{"id": row.id, "entity_id": row.entity_id, "type": row.report_type, "description": row.description, "status": row.status, "is_security_report": row.is_security_report, "created_at": row.created_at, "resolved_at": row.resolved_at, "resolution": row.resolution} for row in rows]}


@router.post("/me/reports", summary="Create a private community or security report")
def create_my_report(payload: CommunityReportCreate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    report_limiter.check(f"community-report:{principal.user.id}")
    try:
        row = create_report(db, principal.user, **payload.model_dump()); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"id": row.id, "status": row.status, "is_security_report": row.is_security_report, "message": "Security reports remain private and follow the repository security policy." if row.is_security_report else "Report created."}


@router.get("/me/community/reputation", summary="Read the authenticated contributor's detailed reputation history")
def my_reputation(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return reputation_summary(db, principal.user.id)


@router.get("/community/review/contributions", summary="Read the restricted reviewer queue")
def review_queue(limit: int = Query(default=30, ge=1, le=100), offset: int = Query(default=0, ge=0, le=10000), principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    try:
        require_role(principal.user, "reviewer", "maintainer", "administrator")
    except Exception as exc:
        rejected(exc)
    rows = db.scalars(select(Contribution).where(Contribution.status.in_(("queued", "under-review", "changes-requested"))).order_by(Contribution.created_at)).all()
    return {"items": [contribution_view(db, row, include_private=True) for row in rows[offset:offset + limit]], "total": len(rows), "limit": limit, "offset": offset}


@router.get("/community/review/contributions/{contribution_id}", summary="Read one restricted review detail")
def review_detail(contribution_id: str, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    try:
        require_role(principal.user, "reviewer", "maintainer", "administrator")
    except Exception as exc:
        rejected(exc)
    return contribution_view(db, reviewer_contribution(db, contribution_id), include_private=True)


@router.post("/community/review/contributions/{contribution_id}/actions", summary="Perform a reviewer lifecycle action")
def review_action(contribution_id: str, payload: ReviewActionRequest, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    review_limiter.check(f"community-review:{principal.user.id}")
    try:
        row = reviewer_action(db, principal.user, reviewer_contribution(db, contribution_id), payload.action, payload.reason); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.post("/community/review/contributions/{contribution_id}/comments", summary="Add a structured reviewer comment")
def review_comment(contribution_id: str, payload: ReviewCommentCreate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    review_limiter.check(f"community-review:{principal.user.id}")
    try:
        row = add_comment(db, principal.user, reviewer_contribution(db, contribution_id), payload.body); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"id": row.id, "body": row.body, "created_at": row.created_at}


@router.post("/community/maintain/contributions/{contribution_id}/actions", summary="Perform a maintainer-only lifecycle action")
def maintain_action(contribution_id: str, payload: ReviewActionRequest, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        row = maintainer_action(db, principal.user, reviewer_contribution(db, contribution_id), payload.action, payload.reason); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.post("/community/maintain/contributions/{contribution_id}/assign", summary="Assign an eligible reviewer with maintainer override")
def maintain_assign_reviewer(contribution_id: str, payload: ReviewerAssignmentRequest, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        row = assign_reviewer(db, principal.user, reviewer_contribution(db, contribution_id), payload.reviewer_id, payload.reason); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return contribution_view(db, row, include_private=True)


@router.post("/community/maintain/contributions/{contribution_id}/github-handoff", summary="Request a server-side controlled Git provider handoff")
def github_handoff(contribution_id: str, payload: GithubHandoffRequest, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    if not payload.confirmation:
        raise HTTPException(status_code=422, detail="handoff confirmation is required")
    try:
        result = handoff_to_git(db, principal.user, reviewer_contribution(db, contribution_id)); db.commit()
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"status": result.status, "message": result.message, "pull_request_url": result.pull_request_url}


@router.get("/community/admin/reports", summary="Read private administrator report queue")
def admin_reports(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    try:
        require_role(principal.user, "maintainer", "administrator")
    except Exception as exc:
        rejected(exc)
    rows = db.scalars(select(CommunityReport).order_by(CommunityReport.created_at.desc())).all()
    return {"items": [{"id": row.id, "reporter_id": row.reporter_id, "entity_id": row.entity_id, "type": row.report_type, "description": row.description, "status": row.status, "is_security_report": row.is_security_report, "created_at": row.created_at} for row in rows]}


@router.post("/community/admin/reports/{report_id}/resolve", summary="Resolve a private report with audit logging")
def admin_resolve_report(report_id: str, payload: ReportResolution, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    row = db.get(CommunityReport, report_id)
    if not row:
        raise HTTPException(status_code=404, detail="report not found")
    try:
        row = resolve_report(db, principal.user, row, status=payload.status, resolution=payload.resolution); db.commit(); db.refresh(row)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"id": row.id, "status": row.status, "resolved_at": row.resolved_at}


@router.post("/community/admin/users/{user_id}/moderation", summary="Suspend or reactivate a user with audit logging")
def admin_moderate(user_id: str, payload: UserModerationRequest, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="user not found")
    try:
        target = moderate_user(db, principal.user, target, status=payload.status, reason=payload.reason); db.commit(); db.refresh(target)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"user_id": target.id, "status": target.status, "suspended_at": target.suspended_at}


@router.post("/community/admin/users/{user_id}/role", summary="Assign a role with administrator-only audit logging")
def admin_role(user_id: str, payload: RoleAssignmentRequest, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="user not found")
    try:
        target = assign_role(db, principal.user, target, role=payload.role, reason=payload.reason); db.commit(); db.refresh(target)
    except Exception as exc:
        db.rollback(); rejected(exc)
    return {"user_id": target.id, "role": target.role}
