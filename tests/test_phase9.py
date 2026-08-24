from __future__ import annotations

import unittest

from search.graph import GraphIntelligence
from search.indexes.index_loader import IndexLoader


class Phase9GraphTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = GraphIntelligence(IndexLoader())

    def test_bounded_neighborhood_and_metadata(self):
        payload = self.graph.neighborhood("nmap", depth=2, node_limit=20, edge_limit=40)
        self.assertEqual(payload["center"]["key"], "tool:nmap")
        self.assertLessEqual(len(payload["nodes"]), 20)
        self.assertLessEqual(len(payload["relationships"]), 40)
        self.assertEqual(payload["graph_version"], self.graph.graph_version)
        with self.assertRaises(ValueError):
            self.graph.neighborhood("nmap", depth=5)
        with self.assertRaises(ValueError):
            self.graph.neighborhood("nmap", node_limit=101)

    def test_paths_prerequisites_impact_and_explanations(self):
        route = self.graph.path("nmap", "firewall")
        self.assertTrue(route["found"])
        self.assertLessEqual(len(route["relationships"]), 25)
        self.assertEqual(self.graph.path("nmap", "nmap")["path"][0]["key"], "tool:nmap")
        self.assertFalse(self.graph.path("nmap", "backup", max_length=1)["found"])
        prerequisites = self.graph.prerequisites("api-security")
        self.assertIn("required", prerequisites)
        impact = self.graph.impact("nmap", depth=2, node_limit=30)
        self.assertLessEqual(sum(len(items) for items in impact["affected"].values()), 30)
        self.assertTrue(all("confidence" in edge for edge in route["relationships"]))

    def test_search_attack_defense_and_orphan_suggestions_are_deterministic(self):
        results = self.graph.graph_search("nmap", limit=10)
        self.assertEqual(results["results"][0]["id"], "nmap")
        self.assertEqual(results["results"][0]["match_type"], "direct")
        mapping = self.graph.attack_defense("sql-injection")
        self.assertEqual(set(mapping).issuperset({"techniques", "vulnerabilities", "detection", "defensive_controls", "mitigations", "labs"}), True)
        orphans = self.graph.orphan_suggestions(limit=10)
        self.assertLessEqual(len(orphans["items"]), 10)
        for row in orphans["items"]:
            self.assertTrue(all(item["status"] == "SUGGESTION ONLY — REQUIRES HUMAN REVIEW" for item in row["suggestions"]))
