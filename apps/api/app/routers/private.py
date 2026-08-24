"""Authenticated Phase 8 private profile and account controls."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.contracts import BookmarkCreate, ChangePasswordRequest, GoalSelection, NoteCreate, NotePatch, ProfilePatch, ProgressUpdate
from ..services.personalization import achievement_rows, add_bookmark, bookmark_rows, delete_goal, evaluate_achievements, goal_rows, note_dict, notes, path_progress, progress_for, recommendations, safe_entity, set_goal, skills, update_progress
from search.graph import GraphIntelligence
from ..services.rate_limit import LocalRateLimiter
from ..services.attempts import user_attempts
from ..state.auth import Principal, clear_session_cookies, csrf_protected, current_principal, issue_session, password_hash, revoke_all, validate_password, verify_password
from ..state.database import get_db
from ..state.models import Bookmark, EntityProgress, LearningGoal, PrivateNote, UserLearningGoal, UserProfile, utcnow

router = APIRouter(tags=["authenticated", "private"])
recommendation_limiter = LocalRateLimiter(limit=30, window_seconds=60)


def profile_response(principal: Principal, profile: UserProfile) -> dict:
    return {
        "user": {
            "id": principal.user.id,
            "email": principal.user.email,
            "email_verified": bool(principal.user.email_verified_at),
            "status": principal.user.status,
            "created_at": principal.user.created_at,
        },
        "preferences": {
            "target_difficulty": profile.target_difficulty,
            "learning_pace": profile.learning_pace,
            "experience_level": profile.experience_level,
        },
    }


@router.get("/me", summary="Read the authenticated user profile")
def me(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    profile = db.get(UserProfile, principal.user.id)
    if not profile:
        profile = UserProfile(user_id=principal.user.id); db.add(profile); db.commit(); db.refresh(profile)
    return profile_response(principal, profile)


@router.patch("/me", summary="Update safe authenticated learner preferences")
def patch_me(payload: ProfilePatch, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    profile = db.get(UserProfile, principal.user.id) or UserProfile(user_id=principal.user.id)
    if payload.target_difficulty is not None:
        profile.target_difficulty = payload.target_difficulty
    if payload.learning_pace is not None:
        profile.learning_pace = payload.learning_pace
    if payload.experience_level is not None:
        profile.experience_level = payload.experience_level
    db.add(profile); db.commit(); db.refresh(profile)
    return profile_response(principal, profile)


@router.post("/me/change-password", summary="Change password and rotate authenticated session")
def change_password(payload: ChangePasswordRequest, response: Response, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    if not verify_password(principal.user.password_hash, payload.current_password):
        raise HTTPException(status_code=401, detail="credentials could not be accepted")
    try:
        new_password = validate_password(payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    principal.user.password_hash = password_hash(new_password)
    principal.user.updated_at = utcnow()
    revoke_all(db, principal.user.id)
    issue_session(db, principal.user, response)
    db.commit()
    return {"message": "password changed and prior sessions revoked", "csrf_required": True}


@router.delete("/me", summary="Delete the authenticated account and all private application state")
def delete_account(response: Response, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    db.delete(principal.user); db.commit(); clear_session_cookies(response)
    return {"message": "account and private application state deleted"}


@router.get("/me/goals", summary="List private learning goals")
def get_goals(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return {"items": goal_rows(db, principal.user.id)}


@router.post("/me/goals", summary="Add or update a private learning goal")
def add_goal(payload: GoalSelection, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        item = set_goal(db, principal.user.id, payload.goal_id, payload.is_primary)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.commit(); return item


@router.delete("/me/goals/{goal_id}", status_code=204, summary="Remove one private learning goal")
def remove_goal(goal_id: str, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    if not delete_goal(db, principal.user.id, goal_id):
        raise HTTPException(status_code=404, detail="goal not found")
    db.commit()


@router.get("/me/progress", summary="List private entity progress")
def get_progress(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    rows = progress_for(db, principal.user.id)
    return {"items": [{"entity_id": item.entity_id, "entity_type": item.entity_type, "knowledge_version": item.knowledge_version, "status": item.status, "confidence": item.confidence, "started_at": item.started_at, "completed_at": item.completed_at, "last_activity_at": item.last_activity_at} for item in rows]}


@router.put("/me/progress", summary="Update private progress against an existing knowledge entity")
def put_progress(payload: ProgressUpdate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        row = update_progress(db, principal.user.id, payload.entity_id, payload.status, payload.confidence)
        new_awards = evaluate_achievements(db, principal.user.id)
    except ValueError as exc:
        raise HTTPException(status_code=422 if "mastered" in str(exc) else 404, detail=str(exc))
    db.commit()
    return {"entity_id": row.entity_id, "status": row.status, "confidence": row.confidence, "knowledge_version": row.knowledge_version, "new_achievements": new_awards}


@router.get("/me/skills", summary="Read deterministic private skill estimates")
def get_skills(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return {"items": skills(db, principal.user.id)}


@router.get("/me/skills/{skill}", summary="Read one deterministic private skill estimate")
def get_skill(skill: str, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    item = next((entry for entry in skills(db, principal.user.id) if entry["skill"] == skill), None)
    if not item:
        raise HTTPException(status_code=404, detail="skill not found")
    return item


@router.get("/me/learning", summary="Read derived private learning-path progress")
def get_learning(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return {"items": path_progress(db, principal.user.id)}


@router.get("/me/bookmarks", summary="List private bookmarks")
def get_bookmarks(type: str | None = Query(default=None), principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return {"items": bookmark_rows(db, principal.user.id, type)}


@router.post("/me/bookmarks", summary="Create a private bookmark for existing knowledge")
def create_bookmark(payload: BookmarkCreate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    try:
        row = add_bookmark(db, principal.user.id, payload.entity_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.commit(); return {"entity_id": row.entity_id, "entity_type": row.entity_type, "created_at": row.created_at}


@router.delete("/me/bookmarks/{entity_id}", status_code=204, summary="Delete a private bookmark")
def delete_bookmark(entity_id: str, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    row = db.scalar(select(Bookmark).where(Bookmark.user_id == principal.user.id, Bookmark.entity_id == entity_id))
    if not row:
        raise HTTPException(status_code=404, detail="bookmark not found")
    db.delete(row); db.commit()


@router.get("/me/notes", summary="List private plain-text notes")
def get_notes(q: str | None = Query(default=None, max_length=128), principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    return {"items": [note_dict(item) for item in notes(db, principal.user.id, q)]}


@router.post("/me/notes", summary="Create a private plain-text note")
def create_note(payload: NoteCreate, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    if payload.entity_id:
        try:
            safe_entity(payload.entity_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="entity not found")
    row = PrivateNote(user_id=principal.user.id, entity_id=payload.entity_id, body=payload.body.strip()); db.add(row); db.commit(); db.refresh(row)
    return note_dict(row)


@router.get("/me/notes/{note_id}", summary="Read one private note")
def get_note(note_id: str, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    row = db.scalar(select(PrivateNote).where(PrivateNote.id == note_id, PrivateNote.user_id == principal.user.id))
    if not row:
        raise HTTPException(status_code=404, detail="note not found")
    return note_dict(row)


@router.patch("/me/notes/{note_id}", summary="Update one private plain-text note")
def patch_note(note_id: str, payload: NotePatch, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    row = db.scalar(select(PrivateNote).where(PrivateNote.id == note_id, PrivateNote.user_id == principal.user.id))
    if not row:
        raise HTTPException(status_code=404, detail="note not found")
    if payload.body is not None:
        row.body = payload.body.strip()
    if payload.entity_id is not None:
        try:
            safe_entity(payload.entity_id)
        except ValueError:
            raise HTTPException(status_code=404, detail="entity not found")
        row.entity_id = payload.entity_id
    db.commit(); db.refresh(row); return note_dict(row)


@router.delete("/me/notes/{note_id}", status_code=204, summary="Delete one private note")
def delete_note(note_id: str, principal: Principal = Depends(csrf_protected), db: Session = Depends(get_db)):
    row = db.scalar(select(PrivateNote).where(PrivateNote.id == note_id, PrivateNote.user_id == principal.user.id))
    if not row:
        raise HTTPException(status_code=404, detail="note not found")
    db.delete(row); db.commit()


@router.get("/me/achievements", summary="Read deterministic private achievements")
def get_achievements(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    items = achievement_rows(db, principal.user.id); db.commit(); return {"items": items}


@router.get("/me/recommendations", summary="Read bounded deterministic private recommendations")
def get_recommendations(limit: int = Query(default=10, ge=1, le=30), goal: str | None = None, difficulty: str | None = None, type: str | None = None, principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    recommendation_limiter.check(f"recommendations:{principal.user.id}")
    items = recommendations(db, principal.user.id, limit, goal, difficulty, type); db.commit(); return {"items": items, "limit": limit}


@router.get("/me/dashboard", summary="Read a bounded private learning dashboard summary")
def dashboard(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    items = recommendations(db, principal.user.id, 5)
    response = {"goals": goal_rows(db, principal.user.id), "skills": skills(db, principal.user.id), "learning": path_progress(db, principal.user.id), "recommendations": items, "achievements": achievement_rows(db, principal.user.id), "bookmarks": bookmark_rows(db, principal.user.id)[:5]}
    db.commit(); return response


@router.get("/me/labs", summary="Read minimal private safe-lab attempt history")
def get_labs(principal: Principal = Depends(current_principal)):
    return {"items": user_attempts(principal.user.id)}


@router.get("/me/knowledge-gaps", summary="Read deterministic owner-scoped gaps for selected generated learning paths")
def knowledge_gaps(principal: Principal = Depends(current_principal), db: Session = Depends(get_db)):
    graph = GraphIntelligence()
    progress_rows = db.scalars(select(EntityProgress).where(EntityProgress.user_id == principal.user.id, EntityProgress.status.in_(("completed", "mastered")))).all()
    completed = {f"{row.entity_type}:{row.entity_id}" for row in progress_rows}
    goals = db.execute(select(UserLearningGoal, LearningGoal).join(LearningGoal, UserLearningGoal.goal_id == LearningGoal.id).where(UserLearningGoal.user_id == principal.user.id)).all()
    items = []
    for user_goal, goal in sorted(goals, key=lambda row: (not row[0].is_primary, row[1].id)):
        path_key = f"learning-path:{goal.learning_path_id}"
        required = [edge["target"] for edge in graph.adjacency.get(path_key, []) if edge["relationship"] == "contains-learning-path"]
        missing: dict[str, dict] = {}
        for key in required:
            route = graph.learning_route(key, completed=completed)
            for step in route["steps"]:
                if step["key"] not in completed:
                    missing[step["key"]] = step
        ranked = sorted(missing.values(), key=lambda item: (item["difficulty"] != "beginner", item["name"].lower(), item["key"]))
        items.append({"goal_id": goal.id, "goal": goal.name, "learning_path_id": goal.learning_path_id, "missing": [{**item, "priority": "high" if item["difficulty"] == "beginner" else "medium", "reason": "Required by the selected generated learning path or its published prerequisite route."} for item in ranked[:25]]})
    return {"items": items, **graph.metadata()}
