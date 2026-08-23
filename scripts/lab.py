#!/usr/bin/env python3
"""CLI for safe, local-fixture Phase 6 labs."""
from pathlib import Path
import argparse, json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from labs.engine.catalog import lab_pages, graph_ids
from labs.engine.definition import definition_paths, load_definition
from labs.engine.lifecycle.manager import LabManager
from labs.engine.validation.safety_validator import validate_definition


def output(value, fmt):
    if fmt == "json": print(json.dumps(value, indent=2, sort_keys=True))
    elif isinstance(value, (dict, list)): print(json.dumps(value, indent=2, sort_keys=True))
    else: print(value)


def validation_report():
    pages = lab_pages(); definitions = []
    for path in definition_paths():
        definition = load_definition(path); errors, warnings = validate_definition(definition, fixture_root=ROOT / "labs" / "fixtures", graph_ids=graph_ids())
        definitions.append({"id": definition.get("id"), "path": definition.get("_path"), "errors": errors, "warnings": warnings})
    return {"total_labs": len(pages), "documentation_only": sum(v["execution_mode"] == "documentation-only" for v in pages.values()), "guided": sum(v["execution_mode"] == "guided" for v in pages.values()), "executable": sum(v["execution_mode"] == "executable" for v in pages.values()), "definitions": definitions, "valid": not any(item["errors"] for item in definitions)}


def main():
    ap = argparse.ArgumentParser(description="Run only safe local-fixture labs")
    ap.add_argument("--state-root", default="/tmp/uht-labs", help="ephemeral runtime state directory")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    info = sub.add_parser("info"); info.add_argument("lab_id")
    sub.add_parser("validate")
    create = sub.add_parser("create"); create.add_argument("lab_id"); create.add_argument("--dry-run", action="store_true")
    for name in ["start", "status", "reset", "stop", "destroy", "evidence", "assess"]:
        cmd = sub.add_parser(name); cmd.add_argument("instance_id")
    run = sub.add_parser("run"); run.add_argument("instance_id"); run.add_argument("task_id")
    args = ap.parse_args()
    try:
        manager = LabManager(args.state_root)
        if args.command == "list":
            catalog = []
            for lab_id, item in sorted(lab_pages().items()): catalog.append(item)
            output(catalog, args.format); return 0
        if args.command == "info":
            definition = manager.definition(args.lab_id); definition.pop("_path", None); output(definition, args.format); return 0
        if args.command == "validate":
            report = validation_report(); output(report, args.format); return 0 if report["valid"] else 1
        if args.command == "create": result = manager.create(args.lab_id, dry_run=args.dry_run)
        elif args.command == "start": result = manager.start(args.instance_id)
        elif args.command == "status": result = manager.status(args.instance_id)
        elif args.command == "reset": result = manager.reset(args.instance_id)
        elif args.command == "stop": result = manager.stop(args.instance_id)
        elif args.command == "destroy": result = manager.destroy(args.instance_id)
        elif args.command == "evidence": result = manager.evidence(args.instance_id)
        elif args.command == "assess": result = manager.assess(args.instance_id)
        elif args.command == "run": result = manager.run_task(args.instance_id, args.task_id)
        output(result, args.format); return 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr); return 1

if __name__ == "__main__": sys.exit(main())
