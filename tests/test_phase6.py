import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from labs.engine.catalog import lab_pages, graph_ids
from labs.engine.definition import definition_paths, load_definition
from labs.engine.lifecycle.manager import LabManager
from labs.engine.validation.safety_validator import validate_definition


class Phase6TestCase(unittest.TestCase):
    def test_inventory_and_definitions_are_safe(self):
        pages = lab_pages()
        self.assertEqual(len(pages), 22)
        self.assertEqual(sum(item["execution_mode"] == "executable" for item in pages.values()), 6)
        self.assertEqual(len(list(definition_paths())), 6)
        for path in definition_paths():
            definition = load_definition(path)
            errors, warnings = validate_definition(definition, fixture_root=ROOT / "labs" / "fixtures", graph_ids=graph_ids())
            self.assertEqual(errors, [], path)
            self.assertEqual(warnings, [], path)

    def test_safety_rejects_unsafe_mutations(self):
        definition = load_definition("dns-resolution-inventory")
        for key, value in [("internet_access", True), ("host_networking", True), ("privileged", True), ("host_mounts", True)]:
            mutated = json.loads(json.dumps(definition)); mutated["safety"][key] = value
            errors, _ = validate_definition(mutated, fixture_root=ROOT / "labs" / "fixtures")
            self.assertTrue(errors, key)
        mutated = json.loads(json.dumps(definition)); mutated["environment"]["resources"]["cpu_limit"] = "unbounded"
        errors, _ = validate_definition(mutated, fixture_root=ROOT / "labs" / "fixtures")
        self.assertTrue(any("cpu_limit" in error for error in errors))
        mutated = json.loads(json.dumps(definition)); mutated["allowed_actions"] = ["run_shell"]
        errors, _ = validate_definition(mutated, fixture_root=ROOT / "labs" / "fixtures")
        self.assertTrue(any("unknown action" in error for error in errors))
        mutated = json.loads(json.dumps(definition)); mutated["targets"][0]["fixture"] = "../../etc/passwd.json"
        errors, _ = validate_definition(mutated, fixture_root=ROOT / "labs" / "fixtures")
        self.assertTrue(any("unsafe fixture" in error for error in errors))

    def test_dry_run_does_not_create_instance(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = LabManager(temp)
            result = manager.create("dns-resolution-inventory", dry_run=True)
            self.assertTrue(result["dry_run"])
            self.assertEqual(manager.list_instances(), [])
            self.assertEqual(list((Path(temp) / "instances").glob("*")), [])

    def test_lifecycle_evidence_assessment_reset_destroy(self):
        with tempfile.TemporaryDirectory() as temp:
            manager = LabManager(temp)
            created = manager.create("dns-resolution-inventory")
            instance = created["instance_id"]
            self.assertEqual(created["state"], "ready")
            with self.assertRaises(ValueError): manager.run_task(instance, "inventory-zone")
            manager.start(instance)
            result = manager.run_task(instance, "inventory-zone")
            self.assertEqual(result["evidence"]["evidence_id"], "dns-observation")
            self.assertEqual(manager.assess(instance)["status"], "passed")
            self.assertEqual(manager.evidence(instance)["validation"], [])
            manager.stop(instance)
            manager.reset(instance)
            self.assertEqual(manager.status(instance)["state"], "ready")
            self.assertEqual(manager.status(instance)["evidence_count"], 0)
            manager.destroy(instance)
            self.assertEqual(manager.status(instance)["state"], "destroyed")
            with self.assertRaises(ValueError): manager.start(instance)

    def test_all_reference_labs_execute_locally(self):
        for path in definition_paths():
            with self.subTest(lab=path.stem), tempfile.TemporaryDirectory() as temp:
                manager = LabManager(temp)
                definition = load_definition(path)
                instance = manager.create(definition["id"])["instance_id"]
                manager.start(instance)
                result = manager.run_task(instance, definition["tasks"][0]["id"])
                self.assertEqual(result["task"]["action"], definition["tasks"][0]["action"])
                self.assertEqual(manager.assess(instance)["status"], "passed")
                manager.destroy(instance)

    def test_generated_phase6_reports_exist(self):
        for filename in ["lab-catalog.json", "lab-health.json", "lab-report.json"]:
            data = json.loads((ROOT / "generated" / filename).read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], "1.0")
        health = json.loads((ROOT / "generated" / "lab-health.json").read_text(encoding="utf-8"))
        self.assertEqual(health["unsafe_executable_labs"], 0)
        self.assertEqual(health["executable_labs"], 6)


if __name__ == "__main__": unittest.main()
