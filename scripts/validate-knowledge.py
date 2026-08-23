#!/usr/bin/env python3
"""Validate typed knowledge-graph references in Markdown/YAML source files."""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []
ALLOWED_VERIFICATION = {"verified", "partially-verified", "needs-review", "deprecated", "unverified"}


def parse_meta(text):
    if not text.startswith("---\n") or "\n---" not in text[4:]:
        return {}
    end = text.find("\n---", 4)
    result, current = {}, None
    for line in text[4:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and current:
            result.setdefault(current, []).append(stripped[2:].strip())
        elif ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if value:
                result[key] = value
                current = None
            else:
                result[key] = []
                current = key
    return result


def collect():
    entities = {k: set() for k in ["tool", "concept", "technique", "technology", "vulnerability", "lab", "learning-path", "defensive-control"]}
    pages = []
    def add(kind, path):
        meta = parse_meta(path.read_text(encoding="utf-8"))
        ident = meta.get("id") or (path.parent.name if kind == "learning-path" else path.stem)
        if ident in entities[kind]: ERRORS.append(f"duplicate {kind} id: {ident}")
        entities[kind].add(ident)
        pages.append((kind, ident, path, meta))
    for p in (ROOT / "tools").glob("**/*.md"):
        if p.name not in {"README.md", "INDEX.md"}: add("tool", p)
    for p in (ROOT / "vulnerabilities").glob("**/*.md"):
        if p.name != "README.md": add("vulnerability", p)
    for p in (ROOT / "labs").glob("**/*.md"):
        if p.name != "README.md": add("lab", p)
    for p in (ROOT / "learning-paths").glob("**/README.md"):
        if p.parent.name != "learning-paths": add("learning-path", p)
    for directory, kind in [("concepts", "concept"), ("techniques", "technique"), ("technologies", "technology"), ("defensive-controls", "defensive-control")]:
        for p in (ROOT / "knowledge" / directory).glob("*.md"):
            if p.name != "README.md": add(kind, p)
    return entities, pages

FIELD_TYPES = {
    "concepts": "concept", "techniques": "technique", "technologies": "technology",
    "related_tools": "tool", "tools": "tool", "related_vulnerabilities": "vulnerability", "vulnerabilities": "vulnerability",
    "related_labs": "lab", "labs": "lab", "learning_paths": "learning-path", "defensive_controls": "defensive-control",
}


def validate_refs(entities, pages):
    for kind, ident, path, meta in pages:
        for field, target_kind in FIELD_TYPES.items():
            values = meta.get(field, [])
            if not isinstance(values, list): values = [values]
            for value in values:
                if value not in entities[target_kind]:
                    ERRORS.append(f"{path}: unknown {target_kind} reference '{value}' in {field}")
        text = path.read_text(encoding="utf-8")
        if kind == "tool":
            match = re.search(r"verification:\s*\n\s+status:\s*([^\n]+)", text[:text.find("\n---", 4)])
            if not match:
                ERRORS.append(f"{path}: missing verification.status")
            elif match.group(1).strip() not in ALLOWED_VERIFICATION:
                ERRORS.append(f"{path}: invalid verification.status {match.group(1).strip()}")
            if "sources:" not in text[:text.find("\n---", 4)]: ERRORS.append(f"{path}: missing sources metadata")


def validate_graph(entities):
    graph_path = ROOT / "generated" / "knowledge-graph.json"
    if not graph_path.exists():
        ERRORS.append("generated/knowledge-graph.json is missing")
        return
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        ERRORS.append(f"generated/knowledge-graph.json is invalid JSON: {exc}")
        return
    node_keys = {(n.get("type"), n.get("id")) for n in graph.get("nodes", [])}
    for node in graph.get("nodes", []):
        if (node.get("type"), node.get("id")) not in node_keys:
            ERRORS.append(f"graph node missing typed identity: {node}")
    for rel in graph.get("relationships", []):
        for side in ("source", "target"):
            value = rel.get(side, "")
            if ":" not in value or tuple(value.split(":", 1)) not in node_keys:
                ERRORS.append(f"graph relationship has unknown {side}: {value}")
    if graph.get("schema_version") != "1.0": ERRORS.append("graph schema_version must be 1.0")


def main():
    entities, pages = collect()
    validate_refs(entities, pages)
    validate_graph(entities)
    if ERRORS:
        print("Knowledge validation failed:")
        print("\n".join(f"- {error}" for error in ERRORS))
        return 1
    print(f"Validated {sum(len(v) for v in entities.values())} typed entities and graph references.")
    return 0

if __name__ == "__main__": sys.exit(main())
