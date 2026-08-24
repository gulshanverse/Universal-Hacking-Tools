"""Minimal authenticated summaries of approved local lab outcomes; raw evidence remains ephemeral."""
from __future__ import annotations

from sqlalchemy import func, select

from ..services.artifacts import artifacts
from ..services.personalization import evaluate_achievements
from ..state.auth import expired, token_hash
from ..state.database import database_ready, sessions
from ..state.models import LabAttempt, LabTaskProgress, SessionRecord, User, utcnow


def user_id_for_session(raw_session: str | None) -> str | None:
    if not raw_session or not database_ready():
        return None
    db = sessions()()
    try:
        row = db.scalar(select(SessionRecord).where(SessionRecord.token_hash == token_hash(raw_session, "session")))
        user = db.get(User, row.user_id) if row and not row.revoked_at and not expired(row.expires_at) else None
        return user.id if user and user.status == "active" else None
    finally:
        db.close()


def begin_attempt(user_id: str | None, lab_id: str) -> None:
    if not user_id or not database_ready():
        return
    db = sessions()()
    try:
        highest = db.scalar(select(func.max(LabAttempt.attempt_number)).where(LabAttempt.user_id == user_id, LabAttempt.lab_id == lab_id)) or 0
        db.add(LabAttempt(user_id=user_id, lab_id=lab_id, knowledge_version=artifacts.version(), status="started", attempt_number=highest + 1))
        db.commit()
    finally:
        db.close()


def record_assessment(user_id: str | None, assessment: dict) -> list[dict]:
    if not user_id or not database_ready() or not assessment.get("lab_id"):
        return []
    db = sessions()()
    try:
        attempt = db.scalar(select(LabAttempt).where(LabAttempt.user_id == user_id, LabAttempt.lab_id == assessment["lab_id"], LabAttempt.status == "started").order_by(LabAttempt.started_at.desc()))
        if not attempt:
            return []
        passed, total = int(assessment.get("passed_criteria", 0)), max(int(assessment.get("total_criteria", 0)), 1)
        attempt.status = "completed" if assessment.get("status") == "passed" else "failed"
        attempt.score, attempt.completed_at = round(passed / total, 3), utcnow()
        for criterion in assessment.get("criteria", []):
            task_id = str(criterion.get("criterion_id", "unknown"))[:128]
            db.add(LabTaskProgress(attempt_id=attempt.id, task_id=task_id, status=criterion.get("status", "failed"), completed_at=utcnow() if criterion.get("status") == "passed" else None))
        newly = evaluate_achievements(db, user_id)
        db.commit()
        return newly
    finally:
        db.close()


def user_attempts(user_id: str) -> list[dict]:
    db = sessions()()
    try:
        rows = list(db.scalars(select(LabAttempt).where(LabAttempt.user_id == user_id).order_by(LabAttempt.started_at.desc())))
        return [{"id": item.id, "lab_id": item.lab_id, "status": item.status, "score": item.score, "attempt_number": item.attempt_number, "started_at": item.started_at, "completed_at": item.completed_at, "knowledge_version": item.knowledge_version} for item in rows]
    finally:
        db.close()
