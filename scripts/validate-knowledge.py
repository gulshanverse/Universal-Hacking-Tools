#!/usr/bin/env python3
"""Validate typed knowledge-graph references in Markdown/YAML source files."""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
ERRORS = []
ALLOWED_VERIFICATION = {"verified", "partially-verified", "needs-review", "deprecated", "unverified"}
ALLOWED_CONFIDENCE = {"high", "medium", "low", "unknown"}
ALLOWED_METHODS = {"official-documentation", "official-repository", "official-website", "maintainer-documentation", "security-standard", "vendor-documentation", "primary-research", "secondary-research", "manual-review", "cross-source-review"}


def parse_meta(text):
    if not text.startswith("---\n") or "\n---" not in text[4:]:
        return {}
    end = text.find("\n---", 4)
    result, current, current_item = {}, None, None
    for line in text[4:end].splitlines():
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if indent >= 2 and stripped.startswith("- ") and current:
            payload = stripped[2:].strip()
            if current == "prerequisites" and ":" in payload:
                key, value = payload.split(":", 1)
                current_item = {key.strip(): value.strip()}
                result.setdefault(current, []).append(current_item)
            else:
                result.setdefault(current, []).append(payload)
                current_item = None
        elif indent >= 4 and current == "prerequisites" and current_item and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_item[key.strip()] = value.strip()
        elif indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if value:
                result[key] = value
                current = None
                current_item = None
            else:
                result[key] = []
                current = key
                current_item = None
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
    "concepts": "concept", "related_concepts": "concept", "techniques": "technique", "related_techniques": "technique", "technologies": "technology", "affected_technologies": "technology",
    "related_tools": "tool", "tools": "tool", "related_vulnerabilities": "vulnerability", "vulnerabilities": "vulnerability",
    "related_labs": "lab", "labs": "lab", "learning_paths": "learning-path", "defensive_controls": "defensive-control",
}
ALLOWED_RELATIONSHIPS = {"uses-concept", "concept-of", "related-to-concept", "concept-related-from", "implements-technique", "technique-of", "related-to-technique", "technique-related-from", "uses-technology", "technology-of", "affects-technology", "technology-affected-by", "related-to-vulnerability", "related-from-vulnerability", "uses-tool", "tool-of", "related-to-tool", "related-from-tool", "related-to-lab", "related-from-lab", "part-of-learning-path", "contains-learning-path", "mitigated-by", "control-for", "teaches-concept", "concept-taught-by", "practices-technique", "technique-practiced-by", "demonstrates-vulnerability", "vulnerability-demonstrated-by", "reinforces-control", "control-reinforced-by", "belongs-to-learning-path", "contains-lab", "requires-prerequisite", "prerequisite-for", "requires-prerequisite-required", "prerequisite-for-required", "requires-prerequisite-recommended", "prerequisite-for-recommended", "requires-prerequisite-helpful", "prerequisite-for-helpful", "related-from"}


def validate_refs(entities, pages):
    for kind, ident, path, meta in pages:
        for field, target_kind in FIELD_TYPES.items():
            values = meta.get(field, [])
            if not isinstance(values, list): values = [values]
            for value in values:
                if value not in entities[target_kind]:
                    ERRORS.append(f"{path}: unknown {target_kind} reference '{value}' in {field}")
        prerequisite_values = meta.get("prerequisites", [])
        if not isinstance(prerequisite_values, list): prerequisite_values = [prerequisite_values]
        all_ids = set().union(*entities.values())
        seen_prerequisites = set()
        for value in prerequisite_values:
            target = value.get("target", "") if isinstance(value, dict) else value
            prerequisite_type = value.get("type", "required") if isinstance(value, dict) else "required"
            if target not in all_ids: ERRORS.append(f"{path}: unknown prerequisite reference '{target}'")
            if prerequisite_type not in {"required", "recommended", "helpful"}: ERRORS.append(f"{path}: invalid prerequisite type '{prerequisite_type}'")
            if target in seen_prerequisites: ERRORS.append(f"{path}: duplicate prerequisite '{target}'")
            seen_prerequisites.add(target)
        text = path.read_text(encoding="utf-8")
        front = text[:text.find("\n---", 4)]
        match = re.search(r"verification:\s*\n\s+status:\s*([^\n]+)", front)
        confidence = re.search(r"verification:\s*\n(?:.*\n)*?\s+confidence:\s*([^\n]*)", front)
        method = re.search(r"verification:\s*\n(?:.*\n)*?\s+verification_method:\s*([^\n]+)", front)
        if not match: ERRORS.append(f"{path}: missing verification.status")
        elif match.group(1).strip() not in ALLOWED_VERIFICATION: ERRORS.append(f"{path}: invalid verification.status {match.group(1).strip()}")
        if not confidence or confidence.group(1).strip() not in ALLOWED_CONFIDENCE: ERRORS.append(f"{path}: invalid or missing verification.confidence")
        if not method or method.group(1).strip() not in ALLOWED_METHODS: ERRORS.append(f"{path}: invalid or missing verification.verification_method")
        if kind == "tool":
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
    seen = set()
    for rel in graph.get("relationships", []):
        key = (rel.get("source"), rel.get("target"), rel.get("relationship"))
        if key in seen: ERRORS.append(f"duplicate graph relationship: {key}")
        seen.add(key)
        if rel.get("relationship") not in ALLOWED_RELATIONSHIPS:
            ERRORS.append(f"unknown graph relationship type: {rel.get('relationship')}")
        if rel.get("source") == rel.get("target"):
            ERRORS.append(f"self-referencing graph relationship: {key}")
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
