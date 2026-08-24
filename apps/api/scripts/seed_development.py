#!/usr/bin/env python3
"""Seed explicitly fake, development-only Phase 8 application state; never run in production."""
from __future__ import annotations

import os
from sqlalchemy import select

from app.services.personalization import ensure_catalog, goal_rows, set_goal
from app.state.auth import password_hash
from app.state.config import settings
from app.state.database import transaction
from app.state.models import LearningGoal, User, UserProfile


def main() -> int:
    if settings().is_production:
        raise SystemExit("development seed data is disabled in production")
    email = "developer@example.test"
    with transaction() as db:
        ensure_catalog(db)
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            user = User(email=email, password_hash=password_hash("development-only-password-change-me"), status="active")
            db.add(user); db.flush(); db.add(UserProfile(user_id=user.id))
        if not goal_rows(db, user.id):
            first_goal = next(iter(db.scalars(select(LearningGoal).order_by(LearningGoal.id))), None)
            if first_goal:
                set_goal(db, user.id, first_goal.id, True)
    print("Seeded developer@example.test with a development-only password; never use this account or password in production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
