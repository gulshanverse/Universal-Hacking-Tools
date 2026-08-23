#!/usr/bin/env python3
"""Validate Phase 6 lab classifications and executable definitions offline."""
from pathlib import Path
import argparse, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = ROOT / "labs"
FIXTURE_ROOT = LAB_ROOT / "fixtures"
sys.path.insert(0, str(ROOT))
from labs.engine.definition import definition_paths, load_definition
from labs.engine.validation.safety_validator import EXECUTION_MODES, validate_definition


def parse_flat_frontmatter(text):
    if not text.startswith("---\n") or "\n---" not in text[4:]: return {}
    end = text.find("\n---", 4); result = {}
    for line in text[4:end].splitlines():
        if line.startswith("  ") or ":" not in line: continue
        key, value = line.split(":", 1); result[key.strip()] = value.strip()
    return result


def lab_pages():
    result = {}
    for path in sorted(LAB_ROOT.glob("**/*.md")):
        if path.name == "README.md": continue
        meta = parse_flat_frontmatter(path.read_text(encoding="utf-8"))
        lab_id = meta.get("id") or path.stem
        result[lab_id] = {"id": lab_id, "path": path.relative_to(ROOT).as_posix(), "execution_mode": meta.get("execution_mode", "")}
    return result


def graph_ids():
    path = ROOT / "generated" / "knowledge-graph.json"
    if not path.exists(): return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {f"{item.get('type')}:{item.get('id')}" for item in data.get("nodes", [])}


def validate():
    errors, warnings = [], []
    pages = lab_pages()
    modes = {mode: [] for mode in sorted(EXECUTION_MODES)}
    for lab_id, page in pages.items():
        mode = page["execution_mode"]
        if mode not in EXECUTION_MODES: errors.append(f"{page['path']}: execution_mode must be documentation-only, guided, or executable")
        else: modes[mode].append(lab_id)
    definitions = []
    definition_ids = set()
    ids = graph_ids()
    for path in definition_paths():
        try: definition = load_definition(path)
        except ValueError as exc: errors.append(str(exc)); continue
        definition_id = definition.get("id", path.stem)
        definitions.append(definition)
        if definition_id in definition_ids: errors.append(f"duplicate executable definition: {definition_id}")
        definition_ids.add(definition_id)
        if definition_id not in pages: errors.append(f"definition has no Markdown lab page: {definition_id}")
        elif pages[definition_id]["execution_mode"] != "executable": errors.append(f"definition {definition_id} is not classified executable")
        definition_errors, definition_warnings = validate_definition(definition, fixture_root=FIXTURE_ROOT, graph_ids=ids)
        errors.extend(f"{definition_id}: {error}" for error in definition_errors)
        warnings.extend(f"{definition_id}: {warning}" for warning in definition_warnings)
    for lab_id in modes["executable"]:
        if lab_id not in definition_ids: errors.append(f"executable lab has no definition: {lab_id}")
    for path in sorted(FIXTURE_ROOT.glob("**/*.json")):
        try: value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc: errors.append(f"{path.relative_to(ROOT)}: invalid fixture JSON ({exc})"); continue
        if not isinstance(value, dict): errors.append(f"{path.relative_to(ROOT)}: fixture must be an object")
        if re.search(r"BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}", json.dumps(value), re.IGNORECASE): errors.append(f"{path.relative_to(ROOT)}: secret-like fixture content")
    report = {"schema_version": "1.0", "total_labs": len(pages), "documentation_only": len(modes["documentation-only"]), "guided": len(modes["guided"]), "executable": len(modes["executable"]), "definitions": len(definitions), "valid": not errors, "errors": sorted(set(errors)), "warnings": sorted(set(warnings)), "classified": {key: sorted(value) for key, value in modes.items()}}
    return report


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--format", choices=["text", "json"], default="text"); args = ap.parse_args()
    report = validate()
    if args.format == "json": print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Labs checked: {report['total_labs']}")
        print(f"Documentation-only: {report['documentation_only']}")
        print(f"Guided: {report['guided']}")
        print(f"Executable: {report['executable']}")
        print(f"Definitions: {report['definitions']}")
        print(f"Valid: {report['valid']}")
        if report["warnings"]: print("Warnings:\n" + "\n".join(f"- {item}" for item in report["warnings"]))
        if report["errors"]: print("Errors:\n" + "\n".join(f"- {item}" for item in report["errors"]))
    return 0 if report["valid"] else 1

if __name__ == "__main__": sys.exit(main())
