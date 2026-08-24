"""Phase 8 private-state tests use a disposable isolated database and synthetic accounts only."""
from __future__ import annotations

import os
import tempfile
import unittest
import shutil
from sqlalchemy import func, select
from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
DB_FILE = Path(tempfile.gettempdir()) / "uht-phase8-tests.db"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE}"
os.environ["SESSION_SECRET"] = "phase8-test-session-secret"
os.environ["CSRF_SECRET"] = "phase8-test-csrf-secret"
os.environ["UHT_ENVIRONMENT"] = "test"
LAB_ROOT = Path(tempfile.gettempdir()) / "uht-phase8-test-labs"
os.environ["UHT_LAB_STATE_DIR"] = str(LAB_ROOT)

from app.main import app
from app.routers.auth import auth_limiter
from app.services import personalization
from app.services.email_service import email_service
from app.state.database import configure_database, sessions
from app.state.models import AuditEvent, Bookmark, CommunityProfile, CommunityReport, Contribution, EntityProgress, PrivateNote, SessionRecord, User, UserLearningGoal, UserProfile
from app.services.community import handoff_to_git
from app.services.git_provider import MockGitProvider


class Phase8TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DB_FILE.exists():
            DB_FILE.unlink()
        configure_database(os.environ["DATABASE_URL"])
        shutil.rmtree(LAB_ROOT, ignore_errors=True)
        config = Config(str(ROOT / "apps" / "api" / "alembic.ini"))
        config.set_main_option("script_location", str(ROOT / "apps" / "api" / "alembic"))
        command.upgrade(config, "head")

    @classmethod
    def tearDownClass(cls):
        config = Config(str(ROOT / "apps" / "api" / "alembic.ini"))
        config.set_main_option("script_location", str(ROOT / "apps" / "api" / "alembic"))
        command.downgrade(config, "base")
        if DB_FILE.exists():
            DB_FILE.unlink()
        shutil.rmtree(LAB_ROOT, ignore_errors=True)

    def setUp(self):
        auth_limiter._buckets.clear()
        email_service.clear()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def csrf(self, client: TestClient | None = None) -> dict[str, str]:
        browser = client or self.client
        return {"X-CSRF-Token": browser.cookies.get("uht_csrf")}

    def create_and_verify(self, email: str, password: str = "Synthetic learning password 123!") -> str:
        response = self.client.post("/api/v1/auth/register", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 202)
        message = email_service.latest(email, "verify-email")
        self.assertIsNotNone(message)
        response = self.client.post("/api/v1/auth/verify-email", json={"token": message.token})
        self.assertEqual(response.status_code, 200)
        return password

    def login(self, email: str, password: str) -> None:
        response = self.client.post("/api/v1/auth/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.cookies.get("uht_session"))
        self.assertTrue(self.client.cookies.get("uht_csrf"))

    def test_migration_auth_lifecycle_and_generic_enumeration(self):
        self.assertEqual(self.client.post("/api/v1/auth/register", json={"email": "bad@example.test", "password": "short"}).status_code, 422)
        password = self.create_and_verify("alice@example.test")
        duplicate = self.client.post("/api/v1/auth/register", json={"email": "alice@example.test", "password": password})
        self.assertEqual(duplicate.status_code, 202)
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"email": "alice@example.test", "password": "wrong password"}).status_code, 401)
        self.login("alice@example.test", password)
        self.assertEqual(self.client.get("/api/v1/auth/session").json()["authenticated"], True)
        self.assertEqual(self.client.get("/api/v1/me").status_code, 200)
        missing_csrf = self.client.post("/api/v1/auth/logout")
        self.assertEqual(missing_csrf.status_code, 403)
        self.assertEqual(self.client.post("/api/v1/auth/logout", headers={"X-CSRF-Token": "not-the-cookie-token"}).status_code, 403)
        self.assertEqual(self.client.post("/api/v1/auth/logout", headers=self.csrf()).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/session").json()["authenticated"], False)

    def test_password_reset_change_and_account_deletion(self):
        password = self.create_and_verify("reset@example.test")
        self.login("reset@example.test", password)
        changed = self.client.post("/api/v1/me/change-password", json={"current_password": password, "new_password": "Another synthetic password 456!"}, headers=self.csrf())
        self.assertEqual(changed.status_code, 200)
        self.client.post("/api/v1/auth/request-password-reset", json={"email": "reset@example.test"})
        reset = email_service.latest("reset@example.test", "password-reset")
        self.assertIsNotNone(reset)
        self.assertEqual(self.client.post("/api/v1/auth/reset-password", json={"token": reset.token, "password": "Third synthetic password 789!"}).status_code, 200)
        self.login("reset@example.test", "Third synthetic password 789!")
        user_id = self.client.get("/api/v1/me").json()["user"]["id"]
        self.assertEqual(self.client.post("/api/v1/me/goals", json={"goal_id": "web-security", "is_primary": True}, headers=self.csrf()).status_code, 200)
        self.assertEqual(self.client.put("/api/v1/me/progress", json={"entity_id": "tcp-ip", "status": "completed", "confidence": "high"}, headers=self.csrf()).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/me/bookmarks", json={"entity_id": "nmap"}, headers=self.csrf()).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/me/notes", json={"body": "Synthetic account-deletion note."}, headers=self.csrf()).status_code, 200)
        self.assertEqual(self.client.delete("/api/v1/me", headers=self.csrf()).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/login", json={"email": "reset@example.test", "password": "Third synthetic password 789!"}).status_code, 401)
        self.assertEqual(self.client.get("/api/v1/tools/nmap").status_code, 200)
        with sessions()() as db:
            self.assertIsNone(db.get(User, user_id))
            for model in (UserProfile, UserLearningGoal, EntityProgress, Bookmark, PrivateNote, SessionRecord):
                self.assertEqual(db.scalar(select(func.count()).select_from(model).where(model.user_id == user_id)), 0)

    def test_private_state_csrf_recommendations_and_idor(self):
        password = self.create_and_verify("alice-state@example.test")
        self.login("alice-state@example.test", password)
        self.assertEqual(self.client.post("/api/v1/me/goals", json={"goal_id": "web-security", "is_primary": True}, headers=self.csrf()).status_code, 200)
        progress = self.client.put("/api/v1/me/progress", json={"entity_id": "tcp-ip", "status": "completed", "confidence": "medium"}, headers=self.csrf())
        self.assertEqual(progress.status_code, 200)
        self.assertEqual(self.client.post("/api/v1/me/bookmarks", json={"entity_id": "nmap"}, headers=self.csrf()).status_code, 200)
        note = self.client.post("/api/v1/me/notes", json={"entity_id": "nmap", "body": "<script>alert('unsafe')</script> plain text only"}, headers=self.csrf())
        self.assertEqual(note.status_code, 200)
        note_id = note.json()["id"]
        self.assertIn("<script>", note.json()["body"])
        self.assertEqual(self.client.post("/api/v1/me/notes", json={"body": "x" * 20001}, headers=self.csrf()).status_code, 422)
        recommended = self.client.get("/api/v1/me/recommendations").json()["items"]
        self.assertGreaterEqual(len(recommended), 1)
        self.assertNotIn("tcp-ip", {item["entity"]["id"] for item in recommended})
        self.assertTrue(all(item["verification_status"] != "deprecated" for item in recommended))
        self.assertEqual(self.client.get("/api/v1/me/recommendations", params={"difficulty": "impossible"}).json()["items"], [])
        self.assertEqual(self.client.get("/api/v1/me/recommendations", params={"type": "unknown"}).json()["items"], [])
        self.assertEqual(self.client.get("/api/v1/me/skills").status_code, 200)

        other = TestClient(app)
        try:
            response = other.post("/api/v1/auth/register", json={"email": "bob-state@example.test", "password": "Synthetic learning password 456!"})
            self.assertEqual(response.status_code, 202)
            verification = email_service.latest("bob-state@example.test", "verify-email")
            self.assertEqual(other.post("/api/v1/auth/verify-email", json={"token": verification.token}).status_code, 200)
            self.assertEqual(other.post("/api/v1/auth/login", json={"email": "bob-state@example.test", "password": "Synthetic learning password 456!"}).status_code, 200)
            self.assertEqual(other.get(f"/api/v1/me/notes/{note_id}").status_code, 404)
            self.assertEqual(other.patch(f"/api/v1/me/notes/{note_id}", json={"body": "Bob cannot edit Alice."}, headers=self.csrf(other)).status_code, 404)
            self.assertEqual(other.delete(f"/api/v1/me/notes/{note_id}", headers=self.csrf(other)).status_code, 404)
            self.assertEqual(other.delete("/api/v1/me/bookmarks/nmap", headers=self.csrf(other)).status_code, 404)
            self.assertEqual(other.get("/api/v1/me/bookmarks").json()["items"], [])
            self.assertEqual(other.get("/api/v1/me/goals").json()["items"], [])
        finally:
            other.close()

    def test_database_health_and_public_degraded_boundary(self):
        self.assertEqual(self.client.get("/api/v1/health/database").status_code, 200)
        anonymous = self.client.get("/api/v1/me/bookmarks")
        self.assertEqual(anonymous.status_code, 401)

    def test_nested_deprecated_verification_is_never_recommended(self):
        password = self.create_and_verify("recommendation@example.test")
        self.login("recommendation@example.test", password)
        deprecated = {"id": "deprecated-example", "type": "concept", "name": "Deprecated", "verification": {"status": "deprecated"}}
        with patch.object(personalization.artifacts, "documents", return_value=[deprecated]):
            self.assertEqual(self.client.get("/api/v1/me/recommendations").json()["items"], [])

    def test_auth_rate_limit_and_single_use_verification_token(self):
        response = self.client.post("/api/v1/auth/register", json={"email": "once@example.test", "password": "Synthetic one time password 123!"})
        self.assertEqual(response.status_code, 202)
        token = email_service.latest("once@example.test", "verify-email").token
        self.assertEqual(self.client.post("/api/v1/auth/verify-email", json={"token": token}).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/verify-email", json={"token": token}).status_code, 400)
        auth_limiter._buckets.clear()
        for _ in range(8):
            self.assertEqual(self.client.post("/api/v1/auth/request-password-reset", json={"email": "missing@example.test"}).status_code, 202)
        self.assertEqual(self.client.post("/api/v1/auth/request-password-reset", json={"email": "missing@example.test"}).status_code, 429)

    def test_authenticated_safe_lab_attempt_persists_without_raw_evidence(self):
        password = self.create_and_verify("lab-state@example.test")
        self.login("lab-state@example.test", password)
        headers = {**self.csrf(), "X-Lab-Session": "phase8-synthetic-lab-session"}
        created = self.client.post("/api/v1/labs/dns-resolution-inventory/instances", headers=headers)
        self.assertEqual(created.status_code, 200)
        instance_id = created.json()["instance_id"]
        self.assertEqual(self.client.post(f"/api/v1/lab-instances/{instance_id}/start", headers=headers).status_code, 200)
        self.assertEqual(self.client.post(f"/api/v1/lab-instances/{instance_id}/tasks/inventory-zone/run", headers=headers).status_code, 200)
        evidence = {"task_id": "inventory-zone", "evidence_id": "dns-observation", "value": {"records": ["synthetic.local"]}}
        self.assertEqual(self.client.post(f"/api/v1/lab-instances/{instance_id}/evidence", json=evidence, headers=headers).status_code, 200)
        assessment = self.client.post(f"/api/v1/lab-instances/{instance_id}/assessment/record", headers=headers)
        self.assertEqual(assessment.status_code, 200)
        self.assertEqual(assessment.json()["status"], "passed")
        attempts = self.client.get("/api/v1/me/labs").json()["items"]
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["status"], "completed")
        self.assertNotIn("evidence", attempts[0])
        self.assertIn("first-safe-lab", {item["id"] for item in self.client.get("/api/v1/me/achievements").json()["items"]})
        self.assertEqual(self.client.delete(f"/api/v1/lab-instances/{instance_id}", headers=headers).status_code, 200)

    def test_phase9_graph_api_bounds_export_overlay_and_owner_gaps(self):
        neighborhood = self.client.get("/api/v1/graph/neighborhood", params={"entity": "nmap", "depth": 2, "limit": 20, "edge_limit": 40})
        self.assertEqual(neighborhood.status_code, 200)
        self.assertEqual(neighborhood.json()["center"]["id"], "nmap")
        self.assertLessEqual(len(neighborhood.json()["nodes"]), 20)
        self.assertLessEqual(len(neighborhood.json()["relationships"]), 40)
        self.assertEqual(self.client.get("/api/v1/graph/neighborhood", params={"entity": "nmap", "depth": 5}).status_code, 422)
        self.assertEqual(self.client.get("/api/v1/graph/neighborhood", params={"entity": "nmap", "relationship_type": "invented-link"}).status_code, 422)
        path = self.client.get("/api/v1/graph/path", params={"from": "nmap", "to": "firewall"})
        self.assertEqual(path.status_code, 200); self.assertTrue(path.json()["found"])
        self.assertEqual(self.client.get("/api/v1/graph/impact", params={"entity": "nmap", "depth": 4, "limit": 100}).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/graph/attack-defense", params={"entity": "sql-injection"}).status_code, 200)
        export = self.client.get("/api/v1/graph/export", params={"entity": "nmap", "format": "csv"})
        self.assertEqual(export.status_code, 200); self.assertNotIn("@example.test", export.text)
        self.assertEqual(self.client.get("/api/v1/graph/orphans", params={"limit": 10}).status_code, 200)
        search = self.client.get("/api/v1/search", params={"q": "nmap", "graph_context": "true"})
        self.assertEqual(search.status_code, 200); self.assertEqual(search.json()["results"][0]["match_type"], "direct")

        password = self.create_and_verify("graph-owner@example.test")
        self.login("graph-owner@example.test", password)
        self.assertEqual(self.client.put("/api/v1/me/progress", json={"entity_id": "nmap", "status": "completed", "confidence": "high"}, headers=self.csrf()).status_code, 200)
        overlay = self.client.get("/api/v1/graph/neighborhood", params={"entity": "nmap"})
        self.assertEqual(overlay.status_code, 200)
        self.assertEqual(next(item for item in overlay.json()["nodes"] if item["key"] == "tool:nmap")["learning_state"], "completed")
        self.assertEqual(self.client.post("/api/v1/me/goals", json={"goal_id": "web-security", "is_primary": True}, headers=self.csrf()).status_code, 200)
        gaps = self.client.get("/api/v1/me/knowledge-gaps")
        self.assertEqual(gaps.status_code, 200); self.assertIn("items", gaps.json())

    def test_phase10_contribution_lifecycle_rbac_privacy_and_moderation(self):
        password_a = self.create_and_verify("community-a@example.test")
        self.login("community-a@example.test", password_a)
        profile = self.client.post("/api/v1/me/community/profile", json={"username": "synthetic_contributor", "display_name": "Synthetic Contributor", "bio": "Security documentation contributor", "is_public": True}, headers=self.csrf())
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(self.client.patch("/api/v1/me/community/profile", json={"role": "maintainer"}, headers=self.csrf()).status_code, 422)
        draft = self.client.post("/api/v1/me/contributions", json={"contribution_type": "relationship", "title": "Connect Nmap to Firewall", "description": "A bounded generated-entity relationship proposal.", "proposed_data": {"source_entity": "nmap", "target_entity": "firewall", "relationship": "uses-tool", "reason": "Synthetic test proposal with a reviewer-visible rationale."}}, headers=self.csrf())
        self.assertEqual(draft.status_code, 200)
        contribution_id = draft.json()["id"]
        self.assertEqual(draft.json()["proposed_content_label"], "PROPOSED CONTENT — NOT CANONICAL KNOWLEDGE")
        revised = self.client.patch(f"/api/v1/me/contributions/{contribution_id}", json={"summary": "Clarify synthetic evidence.", "description": "A revised bounded generated-entity relationship proposal."}, headers=self.csrf())
        self.assertEqual(revised.status_code, 200); self.assertEqual(len(revised.json()["versions"]), 2)
        self.assertEqual(self.client.post(f"/api/v1/me/contributions/{contribution_id}/submit", json={"confirmation": True}, headers=self.csrf()).status_code, 200)

        other = TestClient(app)
        reviewer = TestClient(app)
        maintainer = TestClient(app)
        administrator = TestClient(app)
        try:
            for browser, email, password in ((other, "community-b@example.test", "Synthetic community password B 123!"), (reviewer, "community-c@example.test", "Synthetic community password C 123!"), (maintainer, "community-d@example.test", "Synthetic community password D 123!"), (administrator, "community-e@example.test", "Synthetic community password E 123!")):
                self.assertEqual(browser.post("/api/v1/auth/register", json={"email": email, "password": password}).status_code, 202)
                self.assertEqual(browser.post("/api/v1/auth/verify-email", json={"token": email_service.latest(email, "verify-email").token}).status_code, 200)
                self.assertEqual(browser.post("/api/v1/auth/login", json={"email": email, "password": password}).status_code, 200)
            for browser, username in ((other, "synthetic_other"), (reviewer, "synthetic_reviewer"), (maintainer, "synthetic_maintainer"), (administrator, "synthetic_admin")):
                self.assertEqual(browser.post("/api/v1/me/community/profile", json={"username": username, "is_public": True}, headers=self.csrf(browser)).status_code, 200)
            with sessions()() as db:
                for email, role in (("community-c@example.test", "reviewer"), ("community-d@example.test", "maintainer"), ("community-e@example.test", "administrator")):
                    db.scalar(select(User).where(User.email == email)).role = role
                reviewer_user = db.scalar(select(User).where(User.email == "community-c@example.test"))
                db.add(Contribution(user_id=reviewer_user.id, contribution_type="relationship", title="Prior published reviewer work", description="Synthetic published contribution used only to verify deterministic reviewer expertise scoring.", proposed_data={}, status="published", validation={}, duplicate_candidates=[], impact={}, knowledge_version_before="test", knowledge_version_after="test"))
                db.commit()
            self.assertEqual(other.get(f"/api/v1/me/contributions/{contribution_id}").status_code, 404)
            other_update = other.patch(f"/api/v1/me/contributions/{contribution_id}", json={"summary": "attempt", "title": "Other user edit"}, headers=self.csrf(other))
            self.assertEqual(other_update.status_code, 404, other_update.text)
            self.assertEqual(self.client.get("/api/v1/community/review/contributions").status_code, 403)
            reviewer_id = reviewer.get("/api/v1/me").json()["user"]["id"]
            assigned = maintainer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/assign", json={"reviewer_id": reviewer_id, "reason": "Assign the deterministic eligible reviewer."}, headers=self.csrf(maintainer))
            self.assertEqual(assigned.status_code, 200); self.assertEqual(assigned.json()["assigned_reviewer_id"], reviewer_id)
            recommendation = next(item for item in assigned.json()["reviewer_recommendations"] if item["reviewer_id"] == reviewer_id)
            self.assertEqual(recommendation["expertise_matches"], 1)
            self.assertEqual(reviewer.post(f"/api/v1/community/review/contributions/{contribution_id}/actions", json={"action": "reviewer-approved", "reason": "Specific source and relationship context is sufficient for maintainer review."}, headers=self.csrf(reviewer)).status_code, 200)
            self.assertEqual(reviewer.post(f"/api/v1/community/review/contributions/{contribution_id}/comments", json={"body": "<script>unsafe</script>"}, headers=self.csrf(reviewer)).status_code, 422)
            self.assertEqual(reviewer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/actions", json={"action": "maintainer-approved", "reason": "Reviewer cannot finalize."}, headers=self.csrf(reviewer)).status_code, 403)
            approved = maintainer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/actions", json={"action": "maintainer-approved", "reason": "Maintainer accepts the reviewed synthetic proposal."}, headers=self.csrf(maintainer))
            self.assertEqual(approved.status_code, 200); self.assertEqual(approved.json()["status"], "approved")
            failed_handoff = maintainer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/github-handoff", json={"confirmation": True, "reason": "Test unavailable provider behavior."}, headers=self.csrf(maintainer))
            self.assertEqual(failed_handoff.status_code, 200); self.assertEqual(failed_handoff.json()["status"], "failed")
            self.assertEqual(maintainer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/actions", json={"action": "merged", "reason": "No confirmed provider handoff."}, headers=self.csrf(maintainer)).status_code, 422)
            with sessions()() as db:
                row = db.get(Contribution, contribution_id); actor = db.scalar(select(User).where(User.email == "community-d@example.test"))
                self.assertEqual(handoff_to_git(db, actor, row, MockGitProvider("network-timeout")).status, "failed")
                self.assertEqual(row.github_handoff_status, "failed")
                self.assertEqual(handoff_to_git(db, actor, row, MockGitProvider()).status, "created"); db.commit()
            self.assertEqual(maintainer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/actions", json={"action": "merged", "reason": "Mock provider confirmed a pull request."}, headers=self.csrf(maintainer)).status_code, 200)
            published = maintainer.post(f"/api/v1/community/maintain/contributions/{contribution_id}/actions", json={"action": "published", "reason": "Synthetic CI and human review completion."}, headers=self.csrf(maintainer))
            self.assertEqual(published.status_code, 200); self.assertEqual(published.json()["status"], "published")
            public = self.client.get("/api/v1/community/profile/synthetic_contributor")
            self.assertEqual(public.status_code, 200); self.assertNotIn("email", public.json()); self.assertGreaterEqual(public.json()["approved_contributions"], 1)
            report = self.client.post("/api/v1/me/reports", json={"report_type": "security-concern", "entity_id": "nmap", "description": "Synthetic private security report."}, headers=self.csrf())
            self.assertEqual(report.status_code, 200); report_id = report.json()["id"]
            self.assertEqual(other.get("/api/v1/me/reports").json()["items"], [])
            self.assertEqual(administrator.post(f"/api/v1/community/admin/users/{self.client.get('/api/v1/me').json()['user']['id']}/moderation", json={"status": "suspended", "reason": "Synthetic moderation test."}, headers=self.csrf(administrator)).status_code, 200)
            self.assertEqual(self.client.post("/api/v1/me/contributions", json={"contribution_type": "source", "title": "Blocked proposal", "description": "Suspended accounts cannot submit.", "proposed_data": {"source_url": "https://example.test/source", "source_kind": "official", "reason": "test"}}, headers=self.csrf()).status_code, 401)
            self.assertEqual(administrator.post(f"/api/v1/community/admin/reports/{report_id}/resolve", json={"status": "resolved", "resolution": "Synthetic private resolution."}, headers=self.csrf(administrator)).status_code, 200)
            with sessions()() as db:
                self.assertGreater(db.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.target_id == contribution_id)), 0)
                self.assertEqual(db.get(CommunityReport, report_id).status, "resolved")
        finally:
            other.close(); reviewer.close(); maintainer.close(); administrator.close()

    def test_phase10_account_deletion_removes_drafts_preserves_published_history(self):
        password = self.create_and_verify("community-delete@example.test")
        self.login("community-delete@example.test", password)
        self.assertEqual(self.client.post("/api/v1/me/community/profile", json={"username": "synthetic_delete", "is_public": True}, headers=self.csrf()).status_code, 200)
        draft = self.client.post("/api/v1/me/contributions", json={"contribution_type": "source", "title": "Private draft source", "description": "Synthetic draft for deletion test.", "proposed_data": {"source_url": "https://example.test/draft", "source_kind": "official", "reason": "test"}}, headers=self.csrf()).json()["id"]
        user_id = self.client.get("/api/v1/me").json()["user"]["id"]
        with sessions()() as db:
            published = Contribution(user_id=user_id, contribution_type="source", title="Published history", description="Synthetic published history.", proposed_data={}, status="published", validation={}, duplicate_candidates=[], impact={}, knowledge_version_before="test", knowledge_version_after="test")
            db.add(published); db.commit(); published_id = published.id
        self.assertEqual(self.client.delete("/api/v1/me", headers=self.csrf()).status_code, 200)
        with sessions()() as db:
            self.assertIsNone(db.get(Contribution, draft))
            preserved = db.get(Contribution, published_id)
            self.assertIsNotNone(preserved); self.assertIsNone(preserved.user_id)
