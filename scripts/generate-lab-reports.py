#!/usr/bin/env python3
"""Generate deterministic Phase 6 lab catalog and health reports."""
from pathlib import Path
from datetime import date
import argparse, json, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
LAB_ROOT = ROOT / "labs"
AS_OF = date(2026, 8, 23)
sys.path.insert(0, str(ROOT))
from labs.engine.definition import definition_paths, load_definition
from labs.engine.validation.safety_validator import validate_definition
from labs.engine.catalog import lab_pages, graph_ids


def report(as_of=AS_OF):
    pages = lab_pages()
    ids = graph_ids()
    definitions, definition_errors = {}, {}
    for path in definition_paths():
        try:
            definition = load_definition(path)
            definitions[definition["id"]] = definition
            definition_errors[definition["id"]] = validate_definition(definition, fixture_root=LAB_ROOT / "fixtures", graph_ids=ids)[0]
        except ValueError as exc:
            definition_errors[path.stem] = [str(exc)]
    catalog = []
    for lab_id, page in sorted(pages.items()):
        definition = definitions.get(lab_id)
        errors = definition_errors.get(lab_id, [])
        learning = definition.get("learning", {}) if definition else {}
        catalog.append({
            "id": lab_id,
            "name": definition.get("name", lab_id.replace("-", " ").title()) if definition else lab_id.replace("-", " ").title(),
            "path": page["path"],
            "execution_mode": page["execution_mode"],
            "definition": definition.get("_path", "") if definition else "",
            "difficulty": definition.get("difficulty", "") if definition else "",
            "category": definition.get("category", "") if definition else "",
            "safety_valid": bool(definition) and not errors if page["execution_mode"] == "executable" else True,
            "definition_errors": errors,
            "objectives": len(definition.get("objectives", [])) if definition else 0,
            "prerequisites": len(definition.get("prerequisites", [])) if definition else 0,
            "tasks": len(definition.get("tasks", [])) if definition else 0,
            "evidence": len(definition.get("evidence", [])) if definition else 0,
            "assessment_criteria": len(definition.get("assessment", {}).get("criteria", [])) if definition else 0,
            "knowledge_relationship_targets": sum(len(value) for value in learning.values()) if definition else 0,
            "allowed_actions": sorted(definition.get("allowed_actions", [])) if definition else [],
        })
    executable = [item for item in catalog if item["execution_mode"] == "executable"]
    missing = {key: [] for key in ["objectives", "prerequisites", "safety_declarations", "assessment", "cleanup", "evidence", "knowledge_relationships", "unsafe_configuration"]}
    for item in executable:
        definition = definitions.get(item["id"], {})
        if not definition.get("objectives"): missing["objectives"].append(item["id"])
        if "prerequisites" not in definition: missing["prerequisites"].append(item["id"])
        if not definition.get("safety"): missing["safety_declarations"].append(item["id"])
        if not definition.get("assessment", {}).get("criteria"): missing["assessment"].append(item["id"])
        if not definition.get("cleanup"): missing["cleanup"].append(item["id"])
        if not definition.get("evidence"): missing["evidence"].append(item["id"])
        if not any(len(value) for value in definition.get("learning", {}).values()): missing["knowledge_relationships"].append(item["id"])
        if item["definition_errors"]: missing["unsafe_configuration"].append(item["id"])
    safe = sum(1 for item in executable if item["safety_valid"])
    health = {"schema_version": "1.0", "as_of": as_of.isoformat(), "total_labs": len(catalog), "executable_labs": len(executable), "safe_executable_labs": safe, "unsafe_executable_labs": len(executable) - safe, "missing": missing, "valid": not any(missing.values()), "health_score": round(100 * safe / max(1, len(executable)), 2)}
    summary = {"schema_version": "1.0", "as_of": as_of.isoformat(), "total_labs": len(catalog), "documentation_only": sum(item["execution_mode"] == "documentation-only" for item in catalog), "guided": sum(item["execution_mode"] == "guided" for item in catalog), "executable": len(executable), "safe_executable": health["safe_executable_labs"], "unsafe_executable": health["unsafe_executable_labs"], "assessment_coverage": sum(bool(item["assessment_criteria"]) for item in executable), "evidence_coverage": sum(bool(item["evidence"]) for item in executable), "knowledge_relationship_coverage": sum(bool(item["knowledge_relationship_targets"]) for item in executable)}
    return {"schema_version": "1.0", "as_of": as_of.isoformat(), "summary": summary, "labs": catalog}, health


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--as-of", default=AS_OF.isoformat()); args = ap.parse_args()
    catalog, health = report(date.fromisoformat(args.as_of))
    values = {"lab-catalog.json": catalog, "lab-health.json": health, "lab-report.json": {"schema_version": "1.0", "as_of": args.as_of, **catalog["summary"]}}
    before = {name: (OUT / name).read_text(encoding="utf-8") for name in values if (OUT / name).exists()}
    for name, value in values.items(): (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        stale = [name for name in values if name not in before or (OUT / name).read_text(encoding="utf-8") != before[name]]
        if stale: print("Generated lab reports are stale; run python3 scripts/generate-lab-reports.py"); return 1
        print(f"Lab reports are current ({catalog['summary']['total_labs']} labs; {catalog['summary']['executable']} executable).")
    else: print(f"Generated lab reports for {catalog['summary']['total_labs']} labs.")
    return 0

if __name__ == "__main__": sys.exit(main())
