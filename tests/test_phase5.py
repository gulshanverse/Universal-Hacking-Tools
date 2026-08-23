import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class Phase5TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = ROOT / "generated"
        cls.search = json.loads((cls.generated / "search-index.json").read_text())
        cls.trust = json.loads((cls.generated / "trust-report.json").read_text())
        cls.sources = json.loads((cls.generated / "source-catalog.json").read_text())
        cls.claims = json.loads((cls.generated / "claim-report.json").read_text())
        cls.prerequisites = json.loads((cls.generated / "prerequisite-report.json").read_text())
        cls.queue = json.loads((cls.generated / "review-queue.json").read_text())

    def test_all_documents_have_controlled_verification_fields(self):
        statuses = {"verified", "partially-verified", "needs-review", "unverified", "deprecated"}
        confidence = {"high", "medium", "low", "unknown"}
        methods = {"official-documentation", "official-repository", "official-website", "maintainer-documentation", "security-standard", "vendor-documentation", "primary-research", "secondary-research", "manual-review", "cross-source-review"}
        self.assertTrue(self.search["documents"])
        for doc in self.search["documents"]:
            verification = doc["verification"]
            self.assertIn(verification["status"], statuses, doc["id"])
            self.assertIn(verification["confidence"], confidence, doc["id"])
            self.assertIn(verification["verification_method"], methods, doc["id"])

    def test_source_catalog_normalizes_without_invalid_records(self):
        self.assertGreater(self.sources["total_sources"], 0)
        self.assertEqual(self.sources["invalid_sources"], [])
        self.assertGreaterEqual(len(self.sources["duplicate_urls"]), 1)
        for source in self.sources["sources"]:
            self.assertTrue(source["id"])
            self.assertTrue(source["url"])
            self.assertTrue(source["normalized_url"])

    def test_claims_have_complete_traceability(self):
        self.assertGreaterEqual(self.claims["total_claims"], 5)
        self.assertEqual(self.claims["findings"], [])
        for claim in self.claims["claims"]:
            self.assertTrue(claim["entity"])
            self.assertTrue(claim["statement"])
            self.assertTrue(claim["evidence"])

    def test_prerequisite_types_and_cycles(self):
        self.assertGreater(self.prerequisites["required"], 0)
        self.assertGreater(self.prerequisites["recommended"], 0)
        self.assertEqual(self.prerequisites["invalid"], 0)
        self.assertEqual(self.prerequisites["cycles"], [])
        self.assertEqual(self.prerequisites["duplicate_prerequisites"], 0)

    def test_trust_report_is_transparent_and_bounded(self):
        self.assertEqual(self.trust["overall"]["entity_count"], len(self.search["documents"]))
        self.assertTrue(0 <= self.trust["overall"]["trust_score"] <= 100)
        for section in ["source_trust", "claim_trust", "relationship_trust", "prerequisite_trust"]:
            self.assertIn("score", self.trust[section])
            self.assertTrue(0 <= self.trust[section]["score"] <= 100)
        self.assertEqual(self.trust["claim_trust"]["findings"], [])

    def test_review_queue_and_history(self):
        self.assertEqual(self.queue["total_items"], len(self.queue["items"]))
        self.assertGreater(self.queue["total_items"], 0)
        for item in self.queue["items"]:
            self.assertIn(item["priority_level"], {"critical", "high", "medium", "low"})
            self.assertIn(item["recommended_reviewer_type"], {"technical", "documentation", "security", "source-verification", "maintainer"})
            self.assertIn("verification_action", item)
        self.assertTrue(list((ROOT / "verification-history").glob("*.yml")))

    def test_phase5_cli_commands(self):
        trust = subprocess.run([sys.executable, str(ROOT / "scripts/search.py"), "--trust", "--format", "json"], check=True, capture_output=True, text=True)
        queue = subprocess.run([sys.executable, str(ROOT / "scripts/search.py"), "--review-queue", "--format", "json"], check=True, capture_output=True, text=True)
        self.assertIn("overall", json.loads(trust.stdout))
        self.assertIn("items", json.loads(queue.stdout))

if __name__ == "__main__": unittest.main()
