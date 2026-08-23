#!/usr/bin/env python3
"""Generate deterministic completeness, verification, and review reports."""
from pathlib import Path
from datetime import date
import argparse, json, sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
AS_OF = date(2026, 8, 23)
REQUIRED_SECTIONS = {
    "tool": ["Overview", "Purpose", "Key Features", "How It Works", "Installation", "Basic Usage in a Safe Lab", "Intermediate Usage", "Advanced Concepts", "Defensive Perspective", "Detection", "Mitigation", "Alternatives", "Limitations", "References"],
    "vulnerability": ["Description", "Severity and Context", "Root Cause", "Affected Technology", "Preconditions", "Impact", "Safe Attack Concept", "Detection", "Mitigation", "Secure Coding Practices", "Safe Lab", "References"],
    "concept": ["Overview", "Why It Matters", "Core Principles", "Security Relevance", "Defensive Perspective", "References"],
    "technique": ["Overview", "Purpose", "How It Works", "Authorized Lab Usage", "Detection", "Defensive Controls", "Limitations", "References"],
    "technology": ["Overview", "Architecture", "Security Model", "Common Attack Surface", "Security Controls", "Hardening", "References"],
    "defensive-control": ["Overview", "Purpose", "What It Protects", "How It Works", "Limitations", "Monitoring", "References"],
    "lab": ["Objective", "Difficulty", "Prerequisites", "Environment", "Setup", "Learning Goals", "Tasks", "Expected Observations", "Security Interpretation", "Detection", "Mitigation", "Cleanup", "Further Learning"],
    "learning-path": ["Goal", "Prerequisites", "Beginner Stage", "Intermediate Stage", "Advanced Stage", "Concepts", "Techniques", "Tools", "Vulnerabilities", "Labs", "Defensive Knowledge", "Suggested Projects", "Completion Criteria"],
}
REQUIRED_METADATA = {
    "tool": ["name", "slug", "category", "subcategory", "difficulty", "license", "platforms", "language", "repository", "official_website", "documentation", "security_domains", "dual_use", "status"],
    "vulnerability": ["severity", "cwe"],
    "concept": ["id", "type", "name", "status"],
    "technique": ["id", "type", "name", "status"],
    "technology": ["id", "type", "name", "status"],
    "defensive-control": ["id", "type", "name", "status"],
    "lab": ["id", "type", "name", "status"],
    "learning-path": ["id", "type", "name", "status"],
}
TYPE_IMPORTANCE = {"tool": 4, "vulnerability": 5, "concept": 5, "technique": 4, "technology": 3, "defensive-control": 5, "lab": 4, "learning-path": 5}

def parse_frontmatter(text):
    if not text.startswith("---\n") or "\n---" not in text[4:]: return {}
    end = text.find("\n---", 4)
    data = {}
    for line in text[4:end].splitlines():
        if line.startswith("  ") or ":" not in line: continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

def load_docs():
    return json.loads((OUT / "search-index.json").read_text(encoding="utf-8"))["documents"]

def report(as_of=AS_OF, stale_days=180):
    docs = load_docs()
    complete = []
    verification_by_type = {}
    category_counts = {}
    confidence_counts = Counter()
    for doc in docs:
        path = ROOT / doc["path"]
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        meta = parse_frontmatter(text)
        missing_sections = [s for s in REQUIRED_SECTIONS.get(doc["type"], []) if f"## {s}" not in text and f"# {s}" not in text]
        missing_metadata = [m for m in REQUIRED_METADATA.get(doc["type"], []) if not meta.get(m)]
        missing_relationships = [] if doc.get("relationships") else ["relationships"]
        missing_sources = [] if doc.get("sources") else ["sources"]
        verification_meta = doc.get("verification", {})
        status = verification_meta.get("status", "unverified")
        confidence = verification_meta.get("confidence", "unknown")
        last_verified = verification_meta.get("last_verified", "")
        stale = False
        if last_verified:
            try: stale = (as_of - date.fromisoformat(last_verified)).days > stale_days
            except ValueError: stale = True
        score = max(0, round(100 - len(missing_sections) * 5 - len(missing_metadata) * 4 - len(missing_relationships) * 3 - len(missing_sources) * 5 - (2 if status == "needs-review" else 0) - (2 if stale else 0), 2))
        actions = []
        if missing_sources: actions.append("add authoritative source metadata")
        if missing_metadata: actions.append("complete required metadata")
        if missing_sections: actions.append("write missing documentation sections")
        if missing_relationships: actions.append("add justified typed relationships")
        if stale: actions.append("re-verify current upstream facts")
        complete.append({"id": doc["id"], "type": doc["type"], "name": doc["name"], "path": doc["path"], "completeness_score": score, "missing_sections": missing_sections, "missing_metadata": missing_metadata, "missing_relationships": missing_relationships, "missing_sources": missing_sources, "verification_status": status, "confidence": confidence, "stale_verification": stale, "recommended_actions": actions})
        verification_by_type.setdefault(doc["type"], {"total": 0, "verified": 0, "partially_verified": 0, "needs_review": 0, "unverified": 0, "deprecated": 0, "stale": 0, "missing_authoritative_source": 0})
        bucket = verification_by_type[doc["type"]]
        bucket["total"] += 1
        confidence_counts[confidence] += 1
        category_counts.setdefault(doc.get("category", "uncategorized"), {"total": 0, "verified": 0, "partially_verified": 0, "needs_review": 0, "unverified": 0, "deprecated": 0})
        category_counts[doc.get("category", "uncategorized")]["total"] += 1
        key = {"partially-verified": "partially_verified", "needs-review": "needs_review"}.get(status, status)
        if key in bucket: bucket[key] += 1
        if key in category_counts[doc.get("category", "uncategorized")]: category_counts[doc.get("category", "uncategorized")][key] += 1
        if stale: bucket["stale"] += 1
        if not doc.get("sources"): bucket["missing_authoritative_source"] += 1
    complete.sort(key=lambda x: (x["completeness_score"], x["type"], x["id"]))
    queue = []
    for item in complete:
        priority = len(item["missing_sources"]) * 5 + (3 if item["verification_status"] == "needs-review" else 0) + len(item["missing_relationships"]) * 2 + len(item["missing_sections"]) * 2 + (4 if item["stale_verification"] else 0) + TYPE_IMPORTANCE.get(item["type"], 1)
        if priority:
            reviewer = "source-verification" if item["missing_sources"] or item["verification_status"] in {"needs-review", "unverified"} else "documentation" if item["missing_sections"] else "technical"
            level = "critical" if priority >= 20 else "high" if priority >= 12 else "medium" if priority >= 6 else "low"
            queue.append({"priority": priority, "priority_level": level, "id": item["id"], "entity": f"{item['type']}:{item['id']}", "type": item["type"], "name": item["name"], "path": item["path"], "current_status": item["verification_status"], "confidence": item.get("confidence", "unknown"), "missing_sources": item["missing_sources"], "missing_metadata": item["missing_metadata"], "missing_relationships": item["missing_relationships"], "verification_action": item["recommended_actions"], "recommended_reviewer_type": reviewer, "reasons": item["recommended_actions"]})
    queue.sort(key=lambda x: (-x["priority"], x["type"], x["id"]))
    totals = {k: sum(v[k] for v in verification_by_type.values()) for k in ["total", "verified", "partially_verified", "needs_review", "unverified", "deprecated", "stale", "missing_authoritative_source"]}
    claims_path = ROOT / "evidence" / "claims.json"
    claims = json.loads(claims_path.read_text(encoding="utf-8")).get("claims", []) if claims_path.exists() else []
    claims_needing_review = [f"{c.get('entity')}:{c.get('id')}" for c in claims if c.get("status") in {"needs-review", "disputed", "deprecated"}]
    relationships_needing_review = []
    graph_path = OUT / "knowledge-graph.json"
    if graph_path.exists():
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        relationships_needing_review = [f"{r.get('source')}->{r.get('target')}" for r in graph.get("relationships", []) if r.get("relationship") in {"related-to-vulnerability", "related-from-vulnerability", "related-to-technique", "affects-technology", "mitigated-by"}]
    source_authority_counts = Counter()
    source_catalog_path = OUT / "source-catalog.json"
    if source_catalog_path.exists():
        source_catalog = json.loads(source_catalog_path.read_text(encoding="utf-8"))
        source_authority_counts.update(str(item.get("authority", "unknown")) for item in source_catalog.get("sources", []))
    verification_report = {"schema_version": "1.0", "as_of": as_of.isoformat(), "total_entities": len(docs), "totals": totals, "by_entity_type": dict(sorted(verification_by_type.items())), "by_category": dict(sorted(category_counts.items())), "by_status": {k: totals[k] for k in ["verified", "partially_verified", "needs_review", "unverified", "deprecated"]}, "by_confidence": dict(sorted(confidence_counts.items())), "by_source_authority": dict(sorted(source_authority_counts.items())), "stale_verification": [x["id"] for x in complete if x["stale_verification"]], "missing_sources": [x["id"] for x in complete if x["missing_sources"]], "claims_needing_review": claims_needing_review, "relationships_needing_review": relationships_needing_review}
    return {"schema_version": "1.0", "as_of": as_of.isoformat(), "stale_after_days": stale_days, "entities": complete}, verification_report, {"schema_version": "1.0", "as_of": as_of.isoformat(), "total_items": len(queue), "items": queue}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--as-of", default=AS_OF.isoformat()); ap.add_argument("--stale-after-days", type=int, default=180); args = ap.parse_args()
    names = ["content-completeness.json", "verification-report.json", "review-queue.json"]
    before = {n: (OUT / n).read_text(encoding="utf-8") for n in names if (OUT / n).exists()}
    completeness, verification, queue = report(date.fromisoformat(args.as_of), args.stale_after_days)
    values = {names[0]: completeness, names[1]: verification, names[2]: queue}
    for name, value in values.items(): (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        stale = [n for n in names if n not in before or (OUT / n).read_text(encoding="utf-8") != before[n]]
        if stale:
            print("Generated quality reports are stale; run python3 scripts/generate-quality-reports.py"); return 1
        print(f"Quality reports are current ({len(completeness['entities'])} entities; {queue['total_items']} review items).")
    else: print(f"Generated quality reports for {len(completeness['entities'])} entities.")
    return 0
if __name__ == "__main__": sys.exit(main())
