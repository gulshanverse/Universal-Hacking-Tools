"""Shared discovery helpers for Phase 6 lab pages and knowledge IDs."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = ROOT / "labs"


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
