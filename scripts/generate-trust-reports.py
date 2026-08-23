#!/usr/bin/env python3
"""Generate auditable source, claim, trust, and review summaries offline."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date
from urllib.parse import urlsplit, urlunsplit
import argparse, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated"
AS_OF = date(2026, 8, 23)
VALID_STATUSES = {"verified", "partially-verified", "needs-review", "unverified", "deprecated"}
VALID_CONFIDENCE = {"high", "medium", "low", "unknown"}
VALID_METHODS = {"official-documentation", "official-repository", "official-website", "maintainer-documentation", "security-standard", "vendor-documentation", "primary-research", "secondary-research", "manual-review", "cross-source-review"}
VALID_CLAIM_STATUSES = {"verified", "partially-verified", "needs-review", "disputed", "deprecated"}
RELATIONSHIP_REVIEW_TYPES = {"related-to-vulnerability", "related-from-vulnerability", "related-to-technique", "technique-related-from", "demonstrates-vulnerability", "vulnerability-demonstrated-by", "practices-technique", "technique-practiced-by", "reinforces-control", "control-reinforced-by", "affects-technology", "technology-affected-by", "mitigated-by", "control-for"}


def load(name, default):
    path = OUT / name
    if not path.exists(): return default
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_url(url):
    parts = urlsplit(str(url or "").strip())
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def source_records(doc):
    values = doc.get("sources", {})
    if not values: return []
    records = []
    if isinstance(values, dict):
        values = [{"id": key, "title": key.replace("_", " ").title(), "url": value, "type": key.replace("_", "-")} for key, value in values.items()]
    for value in values if isinstance(values, list) else [values]:
        if isinstance(value, dict): record = dict(value)
        else: record = {"url": str(value), "title": str(value), "type": "source"}
        url = str(record.get("url", "")).strip()
        record["url"] = url
        record.setdefault("id", "source-" + hashlib.sha1(normalize_url(url).encode()).hexdigest()[:10])
        record.setdefault("title", record["id"])
        record.setdefault("type", "source")
        host = urlsplit(url).netloc.lower()
        high_domains = ("nist.gov", "cisa.gov", "mitre.org", "owasp.org", "rfc-editor.org", "ietf.org", "cwe.mitre.org")
        if host == "github.com" and urlsplit(url).path.rstrip("/").lower() == "/gulshanverse/universal-hacking-tools":
            record["type"] = "maintainer-documentation"
            record["authority"] = "medium"
            record["notes"] = "Repository-authored structure and exercise provenance; not independent proof of external security facts."
        elif "authority" not in record:
            record["authority"] = "high" if record["type"] in {"official-documentation", "official-repository", "security-standard", "primary-research"} or any(host.endswith(d) for d in high_domains) else "medium" if record["type"] in {"official-website", "vendor-documentation", "maintainer-documentation"} else "unknown"
        record.setdefault("accessed", "")
        record.setdefault("notes", "")
        records.append(record)
    return records


def source_report(docs):
    records, url_groups, title_groups, scheme_groups, findings = [], defaultdict(list), defaultdict(list), defaultdict(list), []
    for doc in docs:
        for record in source_records(doc):
            record = dict(record); record["entity"] = f"{doc['type']}:{doc['id']}"
            record["normalized_url"] = normalize_url(record["url"])
            if not record["url"] or not urlsplit(record["url"]).scheme or not urlsplit(record["url"]).netloc:
                findings.append({"kind": "invalid-url", "entity": record["entity"], "source_id": record["id"], "url": record["url"]})
            if not record.get("accessed"): findings.append({"kind": "missing-access-date", "entity": record["entity"], "source_id": record["id"]})
            if str(record.get("authority", "unknown")) == "unknown": findings.append({"kind": "unknown-authority", "entity": record["entity"], "source_id": record["id"]})
            url_groups[record["normalized_url"]].append(record["entity"])
            parsed = urlsplit(record["normalized_url"])
            scheme_groups[(parsed.netloc, parsed.path, parsed.query)].append((parsed.scheme, record["entity"]))
            title_groups[str(record.get("title", "")).strip().lower()].append(record["entity"])
            records.append(record)
    for url, entities in sorted(url_groups.items()):
        if url and len(entities) > 1: findings.append({"kind": "duplicate-url", "normalized_url": url, "entities": sorted(set(entities))})
    for title, entities in sorted(title_groups.items()):
        if title and len(entities) > 1: findings.append({"kind": "duplicate-title", "title": title, "entities": sorted(set(entities))})
    for key, values in sorted(scheme_groups.items()):
        schemes = sorted(set(scheme for scheme, _ in values))
        if "http" in schemes and "https" in schemes:
            findings.append({"kind": "http-https-variant", "location": key, "schemes": schemes, "entities": sorted(set(entity for _, entity in values))})
    records.sort(key=lambda r: (r["normalized_url"], r["entity"], r["id"]))
    authority = Counter(str(r.get("authority", "unknown")) for r in records)
    return {"schema_version": "1.0", "as_of": AS_OF.isoformat(), "total_sources": len(records), "sources": records, "duplicate_urls": [f for f in findings if f["kind"] == "duplicate-url"], "duplicate_titles": [f for f in findings if f["kind"] == "duplicate-title"], "http_https_variants": [f for f in findings if f["kind"] == "http-https-variant"], "invalid_sources": [f for f in findings if f["kind"] == "invalid-url"], "missing_access_dates": [f for f in findings if f["kind"] == "missing-access-date"], "unknown_authority": [f for f in findings if f["kind"] == "unknown-authority"], "authority_counts": dict(sorted(authority.items()))}


def claims_report(docs, source_catalog):
    claims_data = load_claims()
    entity_keys = {f"{d['type']}:{d['id']}" for d in docs}
    source_urls = {s["normalized_url"] for s in source_catalog["sources"] if s.get("normalized_url")}
    claims, findings, by_status, by_confidence = [], [], Counter(), Counter()
    seen = set()
    for claim in claims_data:
        entity = claim.get("entity", "")
        claim_id = claim.get("id", "")
        key = (entity, claim_id)
        if key in seen: findings.append({"kind": "duplicate-claim-id", "entity": entity, "id": claim_id})
        seen.add(key)
        status, confidence = claim.get("status", ""), claim.get("confidence", "")
        if entity not in entity_keys: findings.append({"kind": "unknown-entity", "entity": entity, "id": claim_id})
        if not claim.get("statement", "").strip(): findings.append({"kind": "empty-statement", "entity": entity, "id": claim_id})
        if status not in VALID_CLAIM_STATUSES: findings.append({"kind": "invalid-status", "entity": entity, "id": claim_id, "value": status})
        if confidence not in VALID_CONFIDENCE: findings.append({"kind": "invalid-confidence", "entity": entity, "id": claim_id, "value": confidence})
        evidence = claim.get("evidence", [])
        if not evidence: findings.append({"kind": "claim-without-evidence", "entity": entity, "id": claim_id})
        for item in evidence:
            source = item.get("source", "") if isinstance(item, dict) else ""
            if not source: findings.append({"kind": "evidence-without-source", "entity": entity, "id": claim_id})
            elif normalize_url(source) not in source_urls: findings.append({"kind": "evidence-source-not-in-catalog", "entity": entity, "id": claim_id, "source": source})
        claims.append(claim)
        by_status[status] += 1; by_confidence[confidence] += 1
    claims.sort(key=lambda c: (c.get("entity", ""), c.get("id", "")))
    return {"schema_version": "1.0", "total_claims": len(claims), "claims": claims, "status_counts": dict(sorted(by_status.items())), "confidence_counts": dict(sorted(by_confidence.items())), "findings": findings}


def load_claims():
    path = ROOT / "evidence" / "claims.json"
    if not path.exists(): return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("claims", [])


def prerequisite_report(graph):
    typed = [(r["source"], r["target"], r.get("relationship", "")) for r in graph.get("relationships", []) if r.get("relationship", "").startswith("requires-prerequisite-")]
    edges = [(source, target) for source, target, _ in typed]
    adjacency = defaultdict(list)
    for source, target in edges: adjacency[source].append(target)
    for key in adjacency: adjacency[key] = sorted(set(adjacency[key]))
    cycles, state, stack = [], {}, []
    def visit(node):
        state[node] = 1; stack.append(node)
        for target in adjacency.get(node, []):
            if state.get(target) == 1:
                start = stack.index(target); cycles.append(stack[start:] + [target])
            elif not state.get(target): visit(target)
        stack.pop(); state[node] = 2
    for node in sorted(adjacency):
        if not state.get(node): visit(node)
    duplicate_edges = len(typed) - len(set(typed))
    counts = {"required": 0, "recommended": 0, "helpful": 0}
    for _, _, label in typed:
        kind = label.rsplit("-", 1)[-1]
        if kind in counts: counts[kind] += 1
    return {"schema_version": "1.0", "required": counts["required"], "recommended": counts["recommended"], "helpful": counts["helpful"], "invalid": 0, "cycles": cycles, "duplicate_prerequisites": duplicate_edges, "edges": [{"source": s, "target": t, "type": label.rsplit("-", 1)[-1]} for s, t, label in sorted(typed)]}


def verification_method(doc):
    method = doc.get("verification", {}).get("verification_method", "manual-review")
    return method if method in VALID_METHODS else "manual-review"


def trust_report():
    search = load("search-index.json", {"documents": []})
    docs, graph = search.get("documents", []), load("knowledge-graph.json", {"relationships": []})
    catalog = source_report(docs)
    claims = claims_report(docs, catalog)
    prerequisites = prerequisite_report(graph)
    lab_report = load("lab-report.json", {})
    lab_health = load("lab-health.json", {})
    claim_by_entity = defaultdict(list)
    for claim in claims["claims"]: claim_by_entity[claim.get("entity", "")].append(claim)
    degree = Counter(r.get("source", "") for r in graph.get("relationships", []))
    entity_trust = []
    for doc in docs:
        key = f"{doc['type']}:{doc['id']}"
        verification = doc.get("verification", {})
        status_score = {"verified": 100, "partially-verified": 70, "needs-review": 35, "unverified": 20, "deprecated": 15}.get(verification.get("status"), 0)
        confidence_score = {"high": 100, "medium": 75, "low": 50, "unknown": 25}.get(verification.get("confidence"), 0)
        source_score = 100 if source_records(doc) else 0
        relation_score = 100 if degree.get(key, 0) else 35
        entity_score = round(status_score * .4 + confidence_score * .2 + source_score * .2 + relation_score * .2, 2)
        entity_trust.append({"entity": key, "name": doc["name"], "type": doc["type"], "trust_score": entity_score, "verification_status": verification.get("status", "unverified"), "confidence": verification.get("confidence", "unknown"), "verification_method": verification_method(doc), "source_count": len(source_records(doc)), "relationship_count": degree.get(key, 0), "claim_count": len(claim_by_entity.get(key, [])), "execution_mode": doc.get("execution_mode", "")})
    entity_trust.sort(key=lambda x: (-x["trust_score"], x["type"], x["entity"]))
    authority_values = {"high": 100, "medium": 75, "low": 50, "unknown": 25}
    all_source_records = [record for doc in docs for record in source_records(doc)]
    source_score = round(sum(authority_values.get(str(record.get("authority", "unknown")), 25) for record in all_source_records) / max(1, len(all_source_records)), 2)
    claim_valid = sum(1 for f in claims["findings"] if f["kind"] in {"claim-without-evidence", "evidence-without-source", "evidence-source-not-in-catalog", "unknown-entity", "invalid-status", "invalid-confidence"})
    claim_score = 100 if not claims["claims"] else round(100 * (len(claims["claims"]) - claim_valid) / len(claims["claims"]), 2)
    relationship_score = round(100 * sum(1 for r in graph.get("relationships", []) if r.get("source") and r.get("target")) / max(1, len(graph.get("relationships", []))), 2)
    prerequisite_score = 100 if not prerequisites["cycles"] and not prerequisites["duplicate_prerequisites"] else 80
    overall = round((source_score + claim_score + relationship_score + prerequisite_score + sum(x["trust_score"] for x in entity_trust) / max(1, len(entity_trust))) / 5, 2)
    return {"schema_version": "1.0", "as_of": AS_OF.isoformat(), "overall": {"trust_score": overall, "entity_count": len(docs), "verified_entities": sum(1 for d in docs if d.get("verification", {}).get("status") == "verified"), "partially_verified_entities": sum(1 for d in docs if d.get("verification", {}).get("status") == "partially-verified"), "needs_review_entities": sum(1 for d in docs if d.get("verification", {}).get("status") == "needs-review"), "unverified_entities": sum(1 for d in docs if d.get("verification", {}).get("status") == "unverified"), "deprecated_entities": sum(1 for d in docs if d.get("verification", {}).get("status") == "deprecated")}, "entity_trust": entity_trust, "source_trust": {"score": source_score, "total_sources": catalog["total_sources"], "authority_counts": catalog["authority_counts"], "duplicate_urls": len(catalog["duplicate_urls"]), "duplicate_titles": len(catalog["duplicate_titles"]), "http_https_variants": len(catalog["http_https_variants"]), "missing_access_dates": len(catalog["missing_access_dates"]), "unknown_authority": len(catalog["unknown_authority"]), "invalid_sources": len(catalog["invalid_sources"])}, "claim_trust": {"score": claim_score, "total_claims": claims["total_claims"], "status_counts": claims["status_counts"], "confidence_counts": claims["confidence_counts"], "findings": claims["findings"]}, "relationship_trust": {"score": relationship_score, "total_relationships": len(graph.get("relationships", [])), "review_required": sum(1 for r in graph.get("relationships", []) if r.get("relationship") in RELATIONSHIP_REVIEW_TYPES)}, "prerequisite_trust": {"score": prerequisite_score, "required": prerequisites["required"], "recommended": prerequisites["recommended"], "helpful": prerequisites["helpful"], "invalid": prerequisites["invalid"], "cycles": prerequisites["cycles"], "duplicate_prerequisites": prerequisites["duplicate_prerequisites"]}, "lab_execution": {"report": lab_report, "health": lab_health, "content_and_execution_are_separate": True}, "source_catalog": catalog, "claims": claims}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); args = ap.parse_args()
    names = ["trust-report.json", "source-catalog.json", "claim-report.json", "prerequisite-report.json"]
    before = {name: (OUT / name).read_text(encoding="utf-8") for name in names if (OUT / name).exists()}
    result = trust_report()
    OUT.mkdir(exist_ok=True)
    (OUT / "trust-report.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "source-catalog.json").write_text(json.dumps(result["source_catalog"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "claim-report.json").write_text(json.dumps(result["claims"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "prerequisite-report.json").write_text(json.dumps(result["prerequisite_trust"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.check:
        stale = [name for name in names if name not in before or (OUT / name).read_text(encoding="utf-8") != before[name]]
        if stale: print("Trust artifacts are stale; run python3 scripts/generate-trust-reports.py"); return 1
        print(f"Trust artifacts are current ({result['overall']['entity_count']} entities; score {result['overall']['trust_score']}%).")
    else: print(f"Generated trust artifacts for {result['overall']['entity_count']} entities.")
    return 0
if __name__ == "__main__": sys.exit(main())
