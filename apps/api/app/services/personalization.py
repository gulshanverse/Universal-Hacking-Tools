"""Deterministic private learning state derived from user records and generated knowledge contracts."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..services.artifacts import artifacts
from ..state.models import Achievement, Bookmark, EntityProgress, LabAttempt, LearningGoal, LearningPathProgress, PrivateNote, RecommendationSnapshot, UserAchievement, UserLearningGoal, UserProfile, utcnow

ACHIEVEMENTS = (
    ("first-safe-lab", "First Safe Lab", "Pass one approved safe local-fixture lab.", {"completed_labs": 1}),
    ("five-safe-labs", "Five Safe Labs Completed", "Pass five approved safe local-fixture labs.", {"completed_labs": 5}),
    ("ten-safe-labs", "Ten Safe Labs Completed", "Pass ten approved safe local-fixture labs.", {"completed_labs": 10}),
    ("learning-path-completed", "Learning Path Completed", "Complete all required entities in one published learning path.", {"completed_learning_paths": 1}),
)
SKILL_KEYS = ("networking", "web-security", "cloud-security", "defensive-security", "digital-forensics", "security-engineering")


def ensure_catalog(db: Session) -> None:
    """Seed only controlled references to existing generated learning paths and deterministic criteria."""
    for path in artifacts.list_entities(entity_type="learning-path"):
        if not db.get(LearningGoal, path["id"]):
            db.add(LearningGoal(id=path["id"], name=path["name"], learning_path_id=path["id"], description=f"Follow the published {path['name']} learning path."))
    for key, name, description, criteria in ACHIEVEMENTS:
        if not db.get(Achievement, key):
            db.add(Achievement(id=key, name=name, description=description, criteria=criteria))
    db.flush()


def safe_entity(entity_id: str, expected_type: str | None = None) -> dict:
    entity = artifacts.resolve(entity_id, expected_type)
    if not entity:
        raise ValueError("unknown entity")
    return entity


def progress_for(db: Session, user_id: str) -> list[EntityProgress]:
    return list(db.scalars(select(EntityProgress).where(EntityProgress.user_id == user_id).order_by(EntityProgress.last_activity_at.desc())))


def update_progress(db: Session, user_id: str, entity_id: str, status: str, confidence: str) -> EntityProgress:
    entity = safe_entity(entity_id)
    if status == "mastered":
        raise ValueError("mastered progress is derived from defined criteria")
    row = db.scalar(select(EntityProgress).where(EntityProgress.user_id == user_id, EntityProgress.entity_id == entity_id))
    now = utcnow()
    if not row:
        row = EntityProgress(user_id=user_id, entity_id=entity_id, entity_type=entity["type"], knowledge_version=artifacts.version(), status=status, confidence=confidence, started_at=now if status != "not-started" else None)
        db.add(row)
    else:
        row.status, row.confidence, row.knowledge_version, row.last_activity_at = status, confidence, artifacts.version(), now
        if status != "not-started" and not row.started_at:
            row.started_at = now
    row.completed_at = now if status == "completed" else None
    db.flush()
    return row


def goal_rows(db: Session, user_id: str) -> list[dict]:
    ensure_catalog(db)
    rows = db.execute(select(UserLearningGoal, LearningGoal).join(LearningGoal, UserLearningGoal.goal_id == LearningGoal.id).where(UserLearningGoal.user_id == user_id).order_by(UserLearningGoal.is_primary.desc(), LearningGoal.name)).all()
    return [{"id": goal.id, "name": goal.name, "learning_path_id": goal.learning_path_id, "description": goal.description, "is_primary": link.is_primary} for link, goal in rows]


def set_goal(db: Session, user_id: str, goal_id: str, primary: bool) -> dict:
    ensure_catalog(db)
    goal = db.get(LearningGoal, goal_id)
    if not goal:
        raise ValueError("unknown learning goal")
    row = db.scalar(select(UserLearningGoal).where(UserLearningGoal.user_id == user_id, UserLearningGoal.goal_id == goal_id))
    if not row:
        row = UserLearningGoal(user_id=user_id, goal_id=goal_id, is_primary=primary); db.add(row)
    else:
        row.is_primary = primary
    if primary:
        db.query(UserLearningGoal).filter(UserLearningGoal.user_id == user_id, UserLearningGoal.goal_id != goal_id).update({UserLearningGoal.is_primary: False}, synchronize_session=False)
    db.flush()
    return {"id": goal.id, "name": goal.name, "learning_path_id": goal.learning_path_id, "description": goal.description, "is_primary": row.is_primary}


def delete_goal(db: Session, user_id: str, goal_id: str) -> bool:
    row = db.scalar(select(UserLearningGoal).where(UserLearningGoal.user_id == user_id, UserLearningGoal.goal_id == goal_id))
    if not row:
        return False
    db.delete(row); db.flush(); return True


def path_progress(db: Session, user_id: str) -> list[dict]:
    completed = {item.entity_id for item in progress_for(db, user_id) if item.status in {"completed", "mastered"}}
    payload: list[dict] = []
    for goal in goal_rows(db, user_id):
        path = safe_entity(goal["learning_path_id"], "learning-path")
        prerequisites = path.get("prerequisites") or []
        required = [item.get("target") if isinstance(item, dict) else item for item in prerequisites]
        total = max(len(required), 1)
        done = sum(1 for item in required if item in completed)
        percentage = round(done / total, 3)
        payload.append({"learning_path_id": path["id"], "name": path["name"], "is_primary": goal["is_primary"], "progress": percentage, "completed_required": done, "total_required": total, "next_prerequisite": next((item for item in required if item not in completed), None)})
    return payload


def _matches_skill(entity: dict, skill: str) -> bool:
    values = " ".join(str(value) for value in [entity.get("category", ""), entity.get("subcategory", ""), entity.get("security_domain", ""), " ".join(entity.get("security_domains", []) or [])]).casefold().replace(" ", "-")
    return skill in values or (skill == "networking" and any(term in values for term in ("network", "dns", "tcp", "tls")))


def skills(db: Session, user_id: str) -> list[dict]:
    completed = {item.entity_id for item in progress_for(db, user_id) if item.status in {"completed", "mastered"}}
    passed_labs = db.scalar(select(func.count(LabAttempt.id)).where(LabAttempt.user_id == user_id, LabAttempt.status == "completed")) or 0
    result: list[dict] = []
    for skill in SKILL_KEYS:
        entities = [item for item in artifacts.documents() if _matches_skill(item, skill) and item.get("verification_status") != "deprecated"]
        total = max(len(entities), 1)
        done = sum(1 for item in entities if item["id"] in completed)
        completion = round(done / total, 3)
        level = "novice" if completion < .15 else "beginner" if completion < .45 else "intermediate" if completion < .75 else "advanced"
        result.append({"skill": skill, "level": level, "completion": completion, "evidence": {"completed_entities": done, "eligible_entities": len(entities), "passed_labs": passed_labs}})
    return result


def add_bookmark(db: Session, user_id: str, entity_id: str) -> Bookmark:
    entity = safe_entity(entity_id)
    row = db.scalar(select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.entity_id == entity_id))
    if row:
        return row
    row = Bookmark(user_id=user_id, entity_id=entity_id, entity_type=entity["type"]); db.add(row); db.flush(); return row


def bookmark_rows(db: Session, user_id: str, entity_type: str | None = None) -> list[dict]:
    query = select(Bookmark).where(Bookmark.user_id == user_id)
    if entity_type:
        query = query.where(Bookmark.entity_type == entity_type)
    rows = list(db.scalars(query.order_by(Bookmark.created_at.desc())))
    return [{"entity": safe_entity(item.entity_id), "created_at": item.created_at} for item in rows if artifacts.resolve(item.entity_id)]


def notes(db: Session, user_id: str, query: str | None = None) -> list[PrivateNote]:
    statement = select(PrivateNote).where(PrivateNote.user_id == user_id)
    if query:
        statement = statement.where(PrivateNote.body.ilike(f"%{query.strip()[:128]}%"))
    return list(db.scalars(statement.order_by(PrivateNote.updated_at.desc())))


def note_dict(note: PrivateNote) -> dict:
    return {"id": note.id, "entity_id": note.entity_id, "body": note.body, "created_at": note.created_at, "updated_at": note.updated_at}


def _completed_labs(db: Session, user_id: str) -> int:
    return db.scalar(select(func.count(LabAttempt.id)).where(LabAttempt.user_id == user_id, LabAttempt.status == "completed")) or 0


def evaluate_achievements(db: Session, user_id: str) -> list[dict]:
    ensure_catalog(db)
    completed_labs = _completed_labs(db, user_id)
    awarded = {item.achievement_id for item in db.scalars(select(UserAchievement).where(UserAchievement.user_id == user_id))}
    newly: list[dict] = []
    for achievement in db.scalars(select(Achievement)):
        needed = int((achievement.criteria or {}).get("completed_labs", 10**9))
        if achievement.id not in awarded and completed_labs >= needed:
            db.add(UserAchievement(user_id=user_id, achievement_id=achievement.id)); newly.append({"id": achievement.id, "name": achievement.name, "description": achievement.description})
    db.flush()
    return newly


def achievement_rows(db: Session, user_id: str) -> list[dict]:
    evaluate_achievements(db, user_id)
    rows = db.execute(select(UserAchievement, Achievement).join(Achievement, UserAchievement.achievement_id == Achievement.id).where(UserAchievement.user_id == user_id).order_by(UserAchievement.awarded_at.desc())).all()
    return [{"id": achievement.id, "name": achievement.name, "description": achievement.description, "criteria": achievement.criteria, "awarded_at": link.awarded_at} for link, achievement in rows]


def verification_status(entity: dict) -> str:
    verification = entity.get("verification")
    return verification.get("status", "needs-review") if isinstance(verification, dict) else "needs-review"


def recommendations(db: Session, user_id: str, limit: int, goal_id: str | None = None, difficulty: str | None = None, entity_type: str | None = None) -> list[dict]:
    complete = {item.entity_id for item in progress_for(db, user_id) if item.status in {"completed", "mastered"}}
    goals = [item for item in goal_rows(db, user_id) if not goal_id or item["id"] == goal_id]
    candidates: list[tuple[dict, dict]] = []
    for goal in goals:
        path = safe_entity(goal["learning_path_id"], "learning-path")
        for item in path.get("prerequisites") or []:
            target = item.get("target") if isinstance(item, dict) else item
            if target and target not in complete and artifacts.resolve(target):
                entity = safe_entity(target)
                candidates.append((entity, {"reason_type": "missing-prerequisite", "reason_entity": target, "reason_text": f"{entity['name']} is a published prerequisite for your {goal['name']} goal."}))
        if path["id"] not in complete:
            candidates.append((path, {"reason_type": "selected-goal", "reason_entity": path["id"], "reason_text": f"Continue the published {goal['name']} learning path."}))
    if not candidates:
        for entity in artifacts.documents():
            if entity["id"] in complete or verification_status(entity) == "deprecated":
                continue
            candidates.append((entity, {"reason_type": "continue-learning", "reason_entity": entity["id"], "reason_text": "This is the next available deterministic learning item."}))
    seen, output = set(), []
    for entity, reason in candidates:
        if entity["id"] in seen or verification_status(entity) == "deprecated":
            continue
        if difficulty and entity.get("difficulty") != difficulty:
            continue
        if entity_type and entity.get("type") != entity_type:
            continue
        if entity.get("type") == "lab" and (entity.get("execution_mode") == "executable" and not entity.get("safety_valid", True)):
            continue
        seen.add(entity["id"])
        output.append({"entity": entity, "explanation": reason, "verification_status": verification_status(entity)})
        if len(output) >= limit:
            break
    db.add(RecommendationSnapshot(user_id=user_id, knowledge_version=artifacts.version(), recommendations=output)); db.flush()
    return output
