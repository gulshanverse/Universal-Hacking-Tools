import os
from unittest.mock import patch
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.state.config import settings, validate_production_secrets


class Phase11ProductionTestCase(unittest.TestCase):
    def production_env(self, **overrides):
        values = {
            "UHT_ENVIRONMENT": "production",
            "DATABASE_URL": "postgresql+psycopg://application:strong-password@db.example.test:5432/uht",
            "SESSION_SECRET": "s" * 48,
            "CSRF_SECRET": "c" * 48,
            "UHT_ALLOWED_ORIGINS": "https://app.example.test",
            "UHT_TRUSTED_HOSTS": "app.example.test",
            "UHT_LAB_STATE_DIR": "/tmp/uht-phase11-production-fixtures",
            "UHT_SECURE_COOKIES": "true",
            "UHT_ENABLE_DOCS": "false",
        }
        values.update(overrides)
        return patch.dict(os.environ, values, clear=False)

    def test_production_configuration_requires_explicit_safe_values(self):
        with self.production_env():
            validate_production_secrets()
            config = settings()
            self.assertTrue(config.secure_cookies)
            self.assertFalse(config.enable_docs)
            self.assertEqual(config.allowed_origins, ("https://app.example.test",))
        with self.production_env(SESSION_SECRET="development-only-change-me"):
            with self.assertRaisesRegex(RuntimeError, "SESSION_SECRET"):
                validate_production_secrets()
        with self.production_env(UHT_ALLOWED_ORIGINS="http://app.example.test"):
            with self.assertRaisesRegex(RuntimeError, "HTTPS"):
                settings()
        with self.production_env(UHT_TRUSTED_HOSTS="*"):
            with self.assertRaisesRegex(RuntimeError, "TRUSTED_HOSTS"):
                settings()

    def test_liveness_headers_and_redacted_validation_details(self):
        client = TestClient(app)
        response = client.get("/api/v1/live", headers={"X-Request-ID": "phase11-request-id"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("version", response.json())
        self.assertEqual(response.headers["x-request-id"], "phase11-request-id")
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        invalid = client.get("/api/v1/knowledge", params={"limit": "not-a-number"})
        self.assertEqual(invalid.status_code, 422)
        issue = invalid.json()["error"]["details"]["issues"][0]
        self.assertNotIn("input", issue)
        self.assertIn("location", issue)
        private = client.get("/api/v1/auth/session")
        self.assertEqual(private.headers["cache-control"], "private, no-store")
