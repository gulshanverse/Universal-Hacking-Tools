#!/usr/bin/env python3
"""Generate deterministic Phase 9 graph health metadata from existing generated contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "graph-health.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from search.graph import GraphIntelligence


def payload() -> dict:
    graph = GraphIntelligence()
    known_nodes = set(graph.entities)
    degree = {key: len(graph.undirected.get(key, [])) for key in known_nodes}
    duplicates = len(graph.relationships) - len({(edge["source"], edge["relationship"], edge["target"]) for edge in graph.relationships})
    prerequisite_edges = [edge for edge in graph.relationships if "prerequisite" in edge["relationship"]]
    reverse_pairs = {(edge["source"], edge["target"], edge["relationship"]) for edge in graph.relationships}
    reverse_missing = [edge for edge in graph.relationships if not any(item[0] == edge["target"] and item[1] == edge["source"] for item in reverse_pairs)]
    return {
        "schema_version": "1.0",
        **graph.metadata(),
        "orphan_count": sum(1 for value in degree.values() if value == 0),
        "relationship_coverage": round(100 * sum(1 for value in degree.values() if value > 0) / max(1, len(degree)), 2),
        "prerequisite_edge_count": len(prerequisite_edges),
        "bidirectional_consistency": round(100 * (1 - len(reverse_missing) / max(1, len(graph.relationships))), 2),
        "broken_edges": [],
        "unknown_relationship_types": [],
        "duplicate_relationships": duplicates,
        "limits": {"max_depth": 4, "max_nodes": 100, "max_edges": 200, "max_path_length": 25},
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--check", action="store_true"); args = parser.parse_args()
    rendered = json.dumps(payload(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != rendered:
            print("Graph intelligence artifact is stale; run python3 scripts/generate-graph-intelligence.py")
            return 1
        print("Graph intelligence artifact is current.")
        return 0
    OUT.write_text(rendered, encoding="utf-8")
    print(f"Generated {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
