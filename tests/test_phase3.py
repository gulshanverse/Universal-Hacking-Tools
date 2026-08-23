import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from search import SearchEngine, DiscoveryEngine, RecommendationEngine, ComparisonEngine, HealthEngine
from search.indexes import IndexLoader, normalize


class Phase3TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loader = IndexLoader(ROOT)
        cls.search = SearchEngine(cls.loader)
        cls.discovery = DiscoveryEngine(cls.loader)

    def test_exact_name_is_first(self):
        result = self.search.search("nmap", limit=5)
        self.assertEqual(result["results"][0]["id"], "nmap")
        self.assertGreaterEqual(result["results"][0]["score"], 100)

    def test_alias_search(self):
        result = self.search.search("XSS", limit=5)
        self.assertEqual(result["results"][0]["id"], "cross-site-scripting")
        self.assertIn("exact alias", result["results"][0]["reasons"])

    def test_partial_and_description_match(self):
        self.assertGreater(self.search.search("packet", limit=10)["total"], 0)
        self.assertGreater(self.search.search("network scanning", limit=10)["total"], 0)

    def test_combined_filters(self):
        result = self.search.search("security", type="tool", category="web security", difficulty="beginner", platform="linux", limit=50)
        self.assertGreater(result["total"], 0)
        for item in result["results"]:
            self.assertEqual(item["type"], "tool")
            self.assertEqual(item["difficulty"].lower(), "beginner")

    def test_category_slug_filter(self):
        result = self.search.search("network", type="tool", category="network-security", difficulty="beginner", platform="linux", limit=10)
        self.assertGreater(result["total"], 0)
        self.assertTrue(all(item["type"] == "tool" for item in result["results"]))

    def test_tokenization(self):
        self.assertEqual(normalize("OWASP ZAP"), normalize("owasp-zap"))
        self.assertEqual(normalize("OWASP_ZAP"), normalize("owasp-zap"))

    def test_direct_and_multihop_discovery(self):
        one = self.discovery.explore("nmap", depth=1)
        two = self.discovery.explore("nmap", depth=2)
        self.assertEqual(one["entity"]["id"], "nmap")
        self.assertGreater(len(one["related"]), 0)
        self.assertGreaterEqual(len(two["related"]), len(one["related"]))
        self.assertEqual(len({f"{x['type']}:{x['id']}" for x in two["related"]}), len(two["related"]))

    def test_paths(self):
        self.assertEqual(self.discovery.find_path("nmap", "nmap"), ["tool:nmap"])
        self.assertTrue(self.discovery.find_path("nmap", "firewall"))
        with self.assertRaises(ValueError): self.discovery.find_path("missing-entity", "nmap")

    def test_recommendations(self):
        result = RecommendationEngine(self.loader).recommend_next("nmap", difficulty="beginner", goals=["network-security"], limit=5)
        self.assertEqual(result["current"]["id"], "nmap")
        self.assertGreater(len(result["recommendations"]), 0)

    def test_comparison(self):
        result = ComparisonEngine(self.loader).compare("nmap", "masscan")
        self.assertEqual(result["tool_a"]["id"], "nmap")
        self.assertEqual(result["tool_b"]["id"], "masscan")
        self.assertIn("platforms", result["comparison"])
        self.assertIn("Not provided", result["benchmarking"])

    def test_health(self):
        report = HealthEngine(self.loader).report()
        self.assertEqual(report["total_entities"], len(self.loader.documents))
        self.assertIn("overall_score", report)
        self.assertIsInstance(report["orphaned_entities"], list)

    def test_json_contracts_and_cli(self):
        for filename in ["search-result.schema.json", "discovery-result.schema.json", "comparison-result.schema.json", "health-report.schema.json"]:
            schema = json.loads((ROOT / "search/schema" / filename).read_text())
            self.assertEqual(schema["type"], "object")
        output = subprocess.run([sys.executable, str(ROOT / "scripts/search.py"), "nmap", "--format", "json"], check=True, capture_output=True, text=True)
        result = json.loads(output.stdout)
        self.assertEqual(result["results"][0]["id"], "nmap")


if __name__ == "__main__":
    unittest.main()
