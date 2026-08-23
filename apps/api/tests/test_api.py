from __future__ import annotations
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT / "apps" / "api"), str(ROOT)]
from fastapi.testclient import TestClient
from app.main import app
from app.services.labs import labs


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.state = tempfile.mkdtemp(prefix="uht-api-test-")
        os.environ["UHT_LAB_STATE_DIR"] = self.state
        labs._manager = None
        labs._sessions = {}
        self.client = TestClient(app)
        self.client.headers.update({"X-Lab-Session": "phase7-test-session"})

    def tearDown(self):
        shutil.rmtree(self.state, ignore_errors=True)

    def test_health_and_readiness(self):
        health = self.client.get("/api/v1/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["entities"], 307)
        self.assertTrue(self.client.get("/api/v1/ready").json()["ready"])
        self.assertEqual(health.headers["x-content-type-options"], "nosniff")

    def test_knowledge_filters_and_detail_errors(self):
        response = self.client.get("/api/v1/knowledge", params={"type": "tool", "difficulty": "beginner", "limit": 5})
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.json()["items"]), 5)
        self.assertTrue(all(item["type"] == "tool" for item in response.json()["items"]))
        missing = self.client.get("/api/v1/knowledge/not-a-real-entity")
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json()["error"]["code"], "ENTITY_NOT_FOUND")
        invalid = self.client.get("/api/v1/knowledge", params={"type": "unknown"})
        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(invalid.json()["error"]["code"], "INVALID_PARAMETER")

    def test_search_discovery_path_recommendations_and_comparison(self):
        search = self.client.get("/api/v1/search", params={"q": "nmap", "limit": 3})
        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.json()["ranking"]["algorithm"], "deterministic")
        self.assertGreater(search.json()["total"], 0)
        related = self.client.get("/api/v1/knowledge/nmap/related", params={"depth": 1, "limit": 10})
        self.assertEqual(related.status_code, 200)
        path = self.client.get("/api/v1/knowledge/path", params={"from": "nmap", "to": "sql-injection"})
        self.assertEqual(path.status_code, 200)
        recommendations = self.client.get("/api/v1/knowledge/nmap/recommendations", params={"limit": 3})
        self.assertEqual(recommendations.status_code, 200)
        comparison = self.client.get("/api/v1/compare", params={"a": "nmap", "b": "wireshark"})
        self.assertEqual(comparison.status_code, 200)
        self.assertIn("benchmarking", comparison.json())

    def test_trust_health_review_and_lab_metadata(self):
        self.assertEqual(self.client.get("/api/v1/trust").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/trust/nmap").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/health/knowledge").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/health/labs").json()["health_score"], 100.0)
        self.assertGreater(self.client.get("/api/v1/review/queue").json()["total"], 0)
        labs_response = self.client.get("/api/v1/labs")
        self.assertEqual(labs_response.json()["total"], 22)
        item = self.client.get("/api/v1/labs/dns-resolution-inventory")
        self.assertEqual(item.status_code, 200)
        self.assertEqual(item.json()["execution_mode"], "executable")
        self.assertIsInstance(item.json()["objectives"], list)
        self.assertIsInstance(item.json()["tasks"], list)

    def test_safe_lab_lifecycle_and_no_generic_execution(self):
        blocked = self.client.post("/api/v1/labs/sql-injection-concepts/instances")
        self.assertEqual(blocked.status_code, 409)
        self.assertEqual(blocked.json()["error"]["code"], "LAB_NOT_EXECUTABLE")
        created = self.client.post("/api/v1/labs/dns-resolution-inventory/instances")
        self.assertEqual(created.status_code, 200)
        instance_id = created.json()["instance_id"]
        self.assertEqual(self.client.post(f"/api/v1/lab-instances/{instance_id}/start").json()["state"], "running")
        evidence = self.client.post(f"/api/v1/lab-instances/{instance_id}/evidence", json={"task_id": "inventory-zone", "evidence_id": "dns-observation", "value": {"records": ["lab.example.test"]}})
        self.assertEqual(evidence.status_code, 200)
        assessment = self.client.get(f"/api/v1/lab-instances/{instance_id}/assessment")
        self.assertEqual(assessment.status_code, 200)
        self.assertEqual(self.client.post(f"/api/v1/lab-instances/{instance_id}/reset").json()["state"], "ready")
        self.assertEqual(self.client.delete(f"/api/v1/lab-instances/{instance_id}").json()["state"], "destroyed")
        self.assertEqual(self.client.post("/api/v1/execute", json={"command": "anything"}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
