#!/usr/bin/env python3
"""Generate deterministic JSON indexes and a typed knowledge graph from Markdown front matter."""
from pathlib import Path
import argparse, json, os, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"

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

def path_for_type(kind, path):
    rel = path.relative_to(ROOT).as_posix()
    if kind == "tool": return path.stem
    if kind == "vulnerability": return path.stem
    if kind == "lab": return path.stem
    if kind == "learning-path": return path.parent.name
    return path.stem

def collect():
    nodes = {}
    def add(kind, path, meta):
        node_id = meta.get("id") or path_for_type(kind, path)
        nodes[(kind, node_id)] = {"id": node_id, "type": kind, "name": meta.get("name", node_id.replace("-", " ").title()), "path": path.relative_to(ROOT).as_posix(), "category": meta.get("category", "")}
    for p in (ROOT / "tools").glob("**/*.md"):
        if p.name not in {"README.md", "INDEX.md"}: add("tool", p, parse_meta(p.read_text(encoding="utf-8")))
    for p in (ROOT / "vulnerabilities").glob("**/*.md"):
        if p.name != "README.md": add("vulnerability", p, parse_meta(p.read_text(encoding="utf-8")))
    for p in (ROOT / "labs").glob("**/*.md"):
        if p.name != "README.md": add("lab", p, parse_meta(p.read_text(encoding="utf-8")))
    for p in (ROOT / "learning-paths").glob("**/README.md"):
        if p.parent.name != "learning-paths":
            add("learning-path", p, parse_meta(p.read_text(encoding="utf-8")))
    for directory, kind in [("concepts", "concept"), ("techniques", "technique"), ("technologies", "technology"), ("defensive-controls", "defensive-control")]:
        for p in (ROOT / "knowledge" / directory).glob("*.md"):
            if p.name != "README.md": add(kind, p, parse_meta(p.read_text(encoding="utf-8")))
    return nodes

def find_source(path, nodes):
    meta = parse_meta(path.read_text(encoding="utf-8"))
    if path.parts[-2] == "tools": kind = "tool"
    elif "tools" in path.parts: kind = "tool"
    elif "vulnerabilities" in path.parts: kind = "vulnerability"
    elif "labs" in path.parts: kind = "lab"
    elif "learning-paths" in path.parts: kind = "learning-path"
    elif "concepts" in path.parts: kind = "concept"
    elif "techniques" in path.parts: kind = "technique"
    elif "technologies" in path.parts: kind = "technology"
    elif "defensive-controls" in path.parts: kind = "defensive-control"
    else: return None, meta
    node_id = meta.get("id") or path_for_type(kind, path)
    return (kind, node_id), meta

TARGET_TYPES = {"concepts": "concept", "techniques": "technique", "technologies": "technology", "related_vulnerabilities": "vulnerability", "vulnerabilities": "vulnerability", "tools": "tool", "related_tools": "tool", "labs": "lab", "related_labs": "lab", "learning_paths": "learning-path", "defensive_controls": "defensive-control", "related_vulnerabilities": "vulnerability"}
RELATION_NAMES = {"concepts": "uses-concept", "techniques": "implements-technique", "technologies": "uses-technology", "related_vulnerabilities": "related-to-vulnerability", "vulnerabilities": "related-to-vulnerability", "tools": "uses-tool", "related_tools": "related-to-tool", "labs": "related-to-lab", "related_labs": "related-to-lab", "learning_paths": "part-of-learning-path", "defensive_controls": "mitigated-by", "sources": "has-source"}

def generate():
    nodes = collect()
    relationships = set()
    for root_dir in [ROOT / "tools", ROOT / "vulnerabilities", ROOT / "labs", ROOT / "learning-paths", ROOT / "knowledge"]:
        for path in root_dir.glob("**/*.md"):
            if path.name in {"README.md", "INDEX.md"}: continue
            source, meta = find_source(path, nodes)
            if source not in nodes: continue
            for field, target_kind in TARGET_TYPES.items():
                values = meta.get(field, [])
                if not isinstance(values, list): values = [values]
                for target_id in values:
                    target = (target_kind, target_id)
                    if target in nodes:
                        relationships.add((source[0], source[1], target_kind, target_id, RELATION_NAMES.get(field, f"related-to-{target_kind}")))
    # Add reverse edges for navigability without changing source metadata.
    reverse = {"uses-concept": "concept-of", "implements-technique": "technique-of", "uses-technology": "technology-of", "related-to-vulnerability": "related-from-vulnerability", "uses-tool": "tool-of", "related-to-tool": "related-from-tool", "related-to-lab": "related-from-lab", "part-of-learning-path": "contains-learning-path", "mitigated-by": "control-for"}
    all_relationships = set(relationships)
    for src_kind, src_id, dst_kind, dst_id, label in relationships:
        all_relationships.add((dst_kind, dst_id, src_kind, src_id, reverse.get(label, "related-from")))
    node_list = sorted(nodes.values(), key=lambda n: (n["type"], n["id"]))
    rel_list = [{"source": f"{a}:{b}", "target": f"{c}:{d}", "relationship": e} for a, b, c, d, e in sorted(all_relationships)]
    graph = {"schema_version": "1.0", "nodes": node_list, "relationships": rel_list}
    OUT.mkdir(exist_ok=True)
    by_type = {"tools": "tool", "vulnerabilities": "vulnerability", "concepts": "concept", "techniques": "technique", "technologies": "technology", "defensive-controls": "defensive-control", "labs": "lab", "learning-paths": "learning-path"}
    for filename, kind in by_type.items():
        data = [n for n in node_list if n["type"] == kind]
        (OUT / f"{filename}.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "knowledge-graph.json").write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return graph

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); args = ap.parse_args()
    before = {}
    if args.check:
        for p in OUT.glob("*.json"):
            before[p.name] = p.read_text(encoding="utf-8")
    graph = generate()
    if args.check:
        stale = [name for name, content in before.items() if not (OUT / name).exists() or (OUT / name).read_text(encoding="utf-8") != content]
        expected = {"tools.json", "vulnerabilities.json", "concepts.json", "techniques.json", "technologies.json", "defensive-controls.json", "labs.json", "learning-paths.json", "knowledge-graph.json"}
        stale += sorted(expected - set(before))
        if stale:
            print("Generated artifacts are stale; run python3 scripts/generate-knowledge.py")
            return 1
        print(f"Generated artifacts are current ({len(graph['nodes'])} nodes, {len(graph['relationships'])} relationships).")
    else:
        print(f"Generated {len(graph['nodes'])} nodes and {len(graph['relationships'])} relationships.")
    return 0
if __name__ == "__main__": sys.exit(main())
