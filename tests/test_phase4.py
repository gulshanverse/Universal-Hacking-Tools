import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

class Phase4TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = ROOT / "generated"
        cls.graph = json.loads((cls.generated / "knowledge-graph.json").read_text())
        cls.search = json.loads((cls.generated / "search-index.json").read_text())
        cls.complete = json.loads((cls.generated / "content-completeness.json").read_text())
        cls.verification = json.loads((cls.generated / "verification-report.json").read_text())
        cls.queue = json.loads((cls.generated / "review-queue.json").read_text())

    def test_expansion_counts(self):
        counts = {}
        for node in self.graph["nodes"]: counts[node["type"]] = counts.get(node["type"], 0) + 1
        self.assertGreaterEqual(counts["tool"], 70)
        self.assertGreaterEqual(counts["vulnerability"], 40)
        self.assertGreaterEqual(counts["concept"], 60)
        self.assertGreaterEqual(counts["technique"], 34)
        self.assertGreaterEqual(counts["technology"], 35)
        self.assertGreaterEqual(counts["defensive-control"], 30)
        self.assertGreaterEqual(counts["lab"], 22)
        self.assertGreaterEqual(counts["learning-path"], 15)

    def test_prerequisite_relationships_are_typed_and_reversible(self):
        labels = {r["relationship"] for r in self.graph["relationships"]}
        self.assertTrue(any(label.startswith("requires-prerequisite-") for label in labels))
        self.assertTrue(any(label.startswith("prerequisite-for-") for label in labels))
        edges = {(r["source"], r["target"], r["relationship"]) for r in self.graph["relationships"]}
        for source, target, label in list(edges):
            if label.startswith("requires-prerequisite-"):
                reverse = "prerequisite-for-" + label.rsplit("-", 1)[-1]
                self.assertIn((target, source, reverse), edges)

    def test_reports_are_complete_and_consistent(self):
        self.assertEqual(len(self.search["documents"]), len(self.complete["entities"]))
        self.assertEqual(self.verification["total_entities"], len(self.search["documents"]))
        self.assertEqual(self.queue["total_items"], len(self.queue["items"]))
        self.assertTrue(all(item["priority"] >= 1 for item in self.queue["items"]))
        self.assertIn("missing_authoritative_source", self.verification["totals"])

    def test_learning_paths_have_depth_sections(self):
        pages = list((ROOT / "learning-paths").glob("*/README.md"))
        self.assertGreaterEqual(len(pages), 15)
        for page in pages:
            text = page.read_text()
            for heading in ["Goal", "Prerequisites", "Beginner Stage", "Intermediate Stage", "Advanced Stage", "Concepts", "Tools", "Labs", "Completion Criteria"]:
                self.assertIn(f"## {heading}", text, page.as_posix())

    def test_new_content_is_safety_bounded(self):
        for path in list((ROOT / "tools").glob("**/*.md")) + list((ROOT / "vulnerabilities").glob("**/*.md")) + list((ROOT / "labs").glob("**/*.md")):
            if path.name in {"README.md", "INDEX.md"}: continue
            text = path.read_text().lower()
            self.assertNotIn("credential theft workflow", text, path.as_posix())
            self.assertNotIn("create malware", text, path.as_posix())

if __name__ == "__main__": unittest.main()
