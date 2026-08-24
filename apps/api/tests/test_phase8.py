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
from app.state.models import Bookmark, EntityProgress, PrivateNote, SessionRecord, User, UserLearningGoal, UserProfile


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
