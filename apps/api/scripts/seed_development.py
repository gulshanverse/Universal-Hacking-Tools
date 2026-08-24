#!/usr/bin/env python3
"""Seed explicitly fake, development-only private application state; never run in production."""
from __future__ import annotations

import os
from sqlalchemy import select

from app.services.personalization import ensure_catalog, goal_rows, set_goal
from app.state.auth import password_hash
from app.state.config import settings
from app.state.database import transaction
from app.state.models import CommunityProfile, LearningGoal, User, UserProfile


def main() -> int:
    if settings().is_production:
        raise SystemExit("development seed data is disabled in production")
    accounts = {
        "developer@example.test": ("contributor", "developer"),
        "reviewer@example.test": ("reviewer", "development_reviewer"),
        "maintainer@example.test": ("maintainer", "development_maintainer"),
        "admin@example.test": ("administrator", "development_admin"),
    }
    with transaction() as db:
        ensure_catalog(db)
        seeded: dict[str, User] = {}
        for email, (role, username) in accounts.items():
            user = db.scalar(select(User).where(User.email == email))
            if not user:
                user = User(email=email, password_hash=password_hash("development-only-password-change-me"), status="active", role=role)
                db.add(user); db.flush(); db.add(UserProfile(user_id=user.id))
            else:
                user.role = role
            if not db.get(CommunityProfile, user.id):
                db.add(CommunityProfile(user_id=user.id, username=username, is_public=email == "developer@example.test", is_hidden=False))
            seeded[email] = user
        user = seeded["developer@example.test"]
        profile = db.get(CommunityProfile, user.id)
        if profile:
            profile.is_public = True
        if not goal_rows(db, user.id):
            first_goal = next(iter(db.scalars(select(LearningGoal).order_by(LearningGoal.id))), None)
            if first_goal:
                set_goal(db, user.id, first_goal.id, True)
    print("Seeded fake development contributor/reviewer/maintainer/administrator accounts at *.example.test with a development-only password; only the synthetic developer profile is public; never use these accounts or password in production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
