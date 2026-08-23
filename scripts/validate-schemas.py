#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"{path}: invalid JSON ({exc})")
        return {}


def required_object(value, fields, label):
    if not isinstance(value, dict):
        ERRORS.append(f"{label}: expected object")
        return
    for field in fields:
        if field not in value:
            ERRORS.append(f"{label}: missing required field {field}")


def validate():
    schema_dir = ROOT / "search" / "schema"
    schemas = {p.stem.replace(".schema", ""): load(p) for p in schema_dir.glob("*.schema.json")}
    claim_schema = load(ROOT / "schemas" / "claim.schema.json")
    schemas["claim"] = claim_schema
    for name, schema in schemas.items():
        required_object(schema, ["$schema", "title", "type", "required", "properties"], f"schema {name}")
    artifacts = {
        "search-result": {"query": "", "filters": {}, "total": 0, "results": []},
        "discovery-result": {"entity": {}, "related": [], "paths": []},
        "comparison-result": {"tool_a": {}, "tool_b": {}, "comparison": {}, "benchmarking": ""},
        "health-report": load(ROOT / "generated" / "knowledge-health.json"),
    }
    for name, value in artifacts.items():
        schema = schemas.get(name, {})
        required_object(value, schema.get("required", []), f"contract {name}")
    search = load(ROOT / "generated" / "search-index.json")
    required_object(search, ["schema_version", "tokenization", "documents"], "generated search-index")
    aliases = load(ROOT / "generated" / "aliases.json")
    required_object(aliases, ["schema_version", "aliases"], "generated aliases")
    graph = load(ROOT / "generated" / "knowledge-graph.json")
    required_object(graph, ["schema_version", "nodes", "relationships"], "generated graph")
    claims = load(ROOT / "generated" / "claim-report.json")
    required_object(claims, ["schema_version", "total_claims", "claims", "findings"], "generated claim report")
    for index, claim in enumerate(claims.get("claims", [])):
        required_object(claim, ["entity", "id", "statement", "evidence", "status", "confidence"], f"claim {index}")


def main():
    validate()
    if ERRORS:
        print("JSON schema validation failed:")
        print("\n".join(f"- {error}" for error in ERRORS))
        return 1
    print("JSON schemas and generated artifact contracts are valid.")
    return 0

if __name__ == "__main__": sys.exit(main())
