#!/usr/bin/env python3
"""Generate normalized search, alias, and health artifacts without external services."""
from pathlib import Path
from datetime import date
import argparse, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
AS_OF = date(2026, 8, 23)
STALE_DAYS = 180
ALIAS_GROUPS = {
    "sql-injection": ["sqli", "sql injection"],
    "cross-site-scripting": ["xss", "cross site scripting"],
    "csrf": ["cross-site request forgery"],
    "mfa": ["multi-factor authentication"],
    "ids-ips": ["ids", "ips", "intrusion detection system", "intrusion prevention system"],
    "owasp-zap": ["zap", "owasp zap"],
    "john-the-ripper": ["john", "jtr"],
    "greenbone-openvas": ["openvas", "greenbone"],
    "volatility3": ["volatility", "volatility 3"],
    "osquery": ["osquery", "os query"],
}

def parse_meta(text):
    if not text.startswith("---\n") or "\n---" not in text[4:]:
        return {}
    end = text.find("\n---", 4)
    data, list_key, map_key = {}, None, None
    for line in text[4:end].splitlines():
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if not stripped:
            continue
        if indent and stripped.startswith("- ") and list_key:
            data.setdefault(list_key, []).append(stripped[2:].strip())
            continue
        if indent and map_key and ":" in stripped:
            key, value = stripped.split(":", 1)
            data.setdefault(map_key, {})[key.strip()] = value.strip()
            continue
        if ":" in line and indent == 0:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if value:
                data[key] = value
                list_key = map_key = None
            elif key in {"verification", "sources"}:
                data[key] = {}
                map_key, list_key = key, None
            else:
                data[key] = []
                list_key, map_key = key, None
    return data

def as_list(value):
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if not value:
        return []
    return [part.strip() for part in re.split(r"[;,]", str(value)) if part.strip()]

def tokens(value):
    if isinstance(value, list):
        value = " ".join(str(x) for x in value)
    value = str(value or "").lower().replace("_", " ").replace("-", " ")
    return sorted(set(re.findall(r"[a-z0-9]+", value)))

def first_description(text, name):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(">"):
            return line.lstrip("> ").strip()
    return f"Documentation for {name}."

def source_paths():
    result = []
    for p in (ROOT / "tools").glob("**/*.md"):
        if p.name not in {"README.md", "INDEX.md"}: result.append(("tool", p))
    for p in (ROOT / "vulnerabilities").glob("**/*.md"):
        if p.name != "README.md": result.append(("vulnerability", p))
    for p in (ROOT / "labs").glob("**/*.md"):
        if p.name != "README.md": result.append(("lab", p))
    for p in (ROOT / "learning-paths").glob("**/README.md"):
        if p.parent.name != "learning-paths": result.append(("learning-path", p))
    for directory, kind in [("concepts", "concept"), ("techniques", "technique"), ("technologies", "technology"), ("defensive-controls", "defensive-control")]:
        for p in (ROOT / "knowledge" / directory).glob("*.md"):
            if p.name != "README.md": result.append((kind, p))
    return result

def node_id(kind, path, meta):
    return meta.get("id") or (path.parent.name if kind == "learning-path" else path.stem)

def aliases_for(doc):
    aliases = []
    key = doc["id"]
    aliases.extend(ALIAS_GROUPS.get(key, []))
    name = doc["name"]
    compact = name.lower().replace("-", " ")
    if compact != name.lower(): aliases.append(compact)
    if key != compact.replace(" ", "-"): aliases.append(key.replace("-", " "))
    return sorted(set(a.lower() for a in aliases if a.lower() != name.lower()))

def generate(as_of=AS_OF, stale_days=STALE_DAYS):
    graph = json.loads((OUT / "knowledge-graph.json").read_text(encoding="utf-8"))
    graph_nodes = {(n["type"], n["id"]): n for n in graph["nodes"]}
    graph_rels = {}
    for rel in graph["relationships"]:
        graph_rels.setdefault(rel["source"], []).append({"target": rel["target"], "relationship": rel["relationship"]})
    docs = []
    for kind, path in source_paths():
        meta = parse_meta(path.read_text(encoding="utf-8"))
        ident = node_id(kind, path, meta)
        node = graph_nodes.get((kind, ident), {"id": ident, "type": kind, "name": meta.get("name", ident.replace("-", " ").title()), "path": path.relative_to(ROOT).as_posix(), "category": meta.get("category", "")})
        verification = meta.get("verification", {}) if isinstance(meta.get("verification"), dict) else {}
        status = verification.get("status") or meta.get("status") or "unverified"
        rels = graph_rels.get(f"{kind}:{ident}", [])
        doc = {
            "id": ident,
            "type": kind,
            "name": node["name"],
            "description": first_description(path.read_text(encoding="utf-8"), node["name"]),
            "path": node["path"],
            "category": meta.get("category", node.get("category", "")),
            "subcategory": meta.get("subcategory", ""),
            "tags": sorted(set(tokens([meta.get("category", ""), meta.get("subcategory", ""), meta.get("security_domains", []), meta.get("concepts", []), meta.get("techniques", []), meta.get("technologies", [])]))),
            "difficulty": meta.get("difficulty", ""),
            "platforms": as_list(meta.get("platforms", [])),
            "security_domains": as_list(meta.get("security_domains", [])),
            "relationships": sorted(rels, key=lambda x: (x["target"], x["relationship"])),
            "prerequisites": as_list(meta.get("prerequisites", [])),
            "verification": {"status": status, "last_verified": verification.get("last_verified", "")},
            "sources": meta.get("sources", {}),
            "license": meta.get("license", ""),
            "dual_use": meta.get("dual_use", ""),
            "keywords": sorted(set(tokens([node["name"], doc if False else "", meta.get("category", ""), meta.get("subcategory", ""), meta.get("security_domains", []), meta.get("concepts", []), meta.get("techniques", []), meta.get("technologies", []), meta.get("related_vulnerabilities", []), meta.get("prerequisites", [])]))),
        }
        doc["aliases"] = aliases_for(doc)
        doc["tokens"] = sorted(set(tokens([doc["name"], doc["description"], doc["category"], doc["subcategory"], doc["tags"], doc["keywords"], doc["aliases"]])))
        docs.append(doc)
    docs.sort(key=lambda d: (d["type"], d["id"]))
    alias_map = {}
    for doc in docs:
        for alias in doc["aliases"]:
            alias_map.setdefault(alias, []).append(f"{doc['type']}:{doc['id']}")
    alias_map = {k: sorted(v) for k, v in sorted(alias_map.items())}
    search = {"schema_version": "1.0", "tokenization": "lowercase whitespace punctuation hyphen underscore normalization", "documents": docs}
    statuses = {s: sum(1 for d in docs if d["verification"]["status"] == s) for s in ["verified", "partially-verified", "needs-review", "unverified", "deprecated"]}
    missing_sources = [f"{d['type']}:{d['id']}" for d in docs if not d["sources"]]
    missing_descriptions = [f"{d['type']}:{d['id']}" for d in docs if not d["description"].strip()]
    missing_relationships = [f"{d['type']}:{d['id']}" for d in docs if not d["relationships"]]
    node_keys = {f"{n['type']}:{n['id']}" for n in graph["nodes"]}
    broken = sorted({f"{r['source']}->{r['target']}" for r in graph["relationships"] if r["source"] not in node_keys or r["target"] not in node_keys})
    degree = {key: 0 for key in node_keys}
    for r in graph["relationships"]:
        degree[r["source"]] = degree.get(r["source"], 0) + 1
    orphaned = sorted(k for k, v in degree.items() if v == 0)
    stale = []
    for d in docs:
        value = d["verification"].get("last_verified", "")
        if value:
            try:
                if (as_of - date.fromisoformat(value)).days > stale_days: stale.append(f"{d['type']}:{d['id']}")
            except ValueError: stale.append(f"{d['type']}:{d['id']}")
    duplicate_aliases = sorted(k for k, v in alias_map.items() if len(v) > 1)
    duplicate_names = sorted(k for k in {d["name"].lower() for d in docs} if sum(1 for d in docs if d["name"].lower() == k) > 1)
    completeness = {
        "documentation": round(100 * (len(docs) - len(missing_descriptions)) / max(1, len(docs)), 2),
        "metadata": round(100 * sum(1 for d in docs if d["type"] and d["name"] and d["path"]) / max(1, len(docs)), 2),
        "relationships": round(100 * (len(docs) - len(missing_relationships)) / max(1, len(docs)), 2),
        "verification": round(100 * (statuses["verified"] + statuses["partially-verified"]) / max(1, len(docs)), 2),
        "sources": round(100 * (len(docs) - len(missing_sources)) / max(1, len(docs)), 2),
        "link_integrity": 100.0 if not broken else 0.0,
    }
    health = {"schema_version": "1.0", "as_of": as_of.isoformat(), "stale_after_days": stale_days, "total_entities": len(docs), "status_counts": statuses, "missing_sources": sorted(missing_sources), "missing_descriptions": sorted(missing_descriptions), "missing_relationships": sorted(missing_relationships), "orphaned_entities": orphaned, "broken_relationships": broken, "stale_verification": sorted(stale), "duplicate_aliases": duplicate_aliases, "duplicate_names": duplicate_names, "scores": completeness, "overall_score": round(sum(completeness.values()) / len(completeness), 2)}
    OUT.mkdir(exist_ok=True)
    (OUT / "search-index.json").write_text(json.dumps(search, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "aliases.json").write_text(json.dumps({"schema_version": "1.0", "aliases": alias_map}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "knowledge-health.json").write_text(json.dumps(health, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return search, health

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--as-of", default=AS_OF.isoformat()); ap.add_argument("--stale-after-days", type=int, default=STALE_DAYS); args = ap.parse_args()
    before = {}
    if args.check:
        for name in ["search-index.json", "aliases.json", "knowledge-health.json"]:
            p = OUT / name
            if p.exists(): before[name] = p.read_text(encoding="utf-8")
    search, health = generate(date.fromisoformat(args.as_of), args.stale_after_days)
    if args.check:
        stale = [name for name, content in before.items() if (OUT / name).read_text(encoding="utf-8") != content]
        missing = [name for name in ["search-index.json", "aliases.json", "knowledge-health.json"] if name not in before]
        if stale or missing:
            print("Generated search artifacts are stale; run python3 scripts/generate-search.py")
            return 1
        print(f"Generated search artifacts are current ({len(search['documents'])} documents; health {health['overall_score']}%).")
    else:
        print(f"Generated search artifacts for {len(search['documents'])} documents.")
    return 0
if __name__ == "__main__": sys.exit(main())
