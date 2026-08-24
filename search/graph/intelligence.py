"""Bounded deterministic graph intelligence; never parses Markdown or mutates knowledge."""
from __future__ import annotations

from collections import deque
from hashlib import sha256
from typing import Any

from ..engine.search_engine import SearchEngine
from ..indexes.index_loader import IndexLoader, normalize, token_set


MAX_DEPTH = 4
MAX_NODES = 100
MAX_EDGES = 200
MAX_PATH_LENGTH = 25
RELATIONSHIP_WEIGHTS = {
    "requires-prerequisite-required": 90,
    "prerequisite-for-required": 90,
    "requires-prerequisite-recommended": 80,
    "prerequisite-for-recommended": 80,
    "requires-prerequisite-helpful": 70,
    "prerequisite-for-helpful": 70,
    "mitigated-by": 85,
    "control-for": 85,
    "demonstrates-vulnerability": 75,
    "vulnerability-demonstrated-by": 75,
    "teaches-concept": 70,
    "concept-taught-by": 70,
    "part-of-learning-path": 65,
    "contains-learning-path": 65,
    "uses-tool": 60,
    "tool-of": 60,
}
CONFIDENCE_WEIGHTS = {"verified": 4, "partially-verified": 3, "needs-review": 2, "unverified": 1, "deprecated": 0}
KNOWN_EXPLANATIONS = {
    "requires-prerequisite": "{source} lists {target} as a {level} prerequisite in the published knowledge graph.",
    "mitigated-by": "{target} is a published defensive control linked to mitigating {source}.",
    "uses-tool": "{source} is linked to {target} through an authored tool relationship.",
    "part-of-learning-path": "{source} is included in the published {target} learning path.",
    "teaches-concept": "The published lab {source} teaches the concept {target}.",
    "demonstrates-vulnerability": "The published lab {source} demonstrates the vulnerability {target} in its declared local-fixture learning mapping.",
}


class GraphIntelligence:
    """Read and reason over an immutable generated graph using stable bounded algorithms."""

    def __init__(self, loader: IndexLoader | None = None):
        self.loader = loader or IndexLoader()
        self.entities = self.loader.entity_map()
        graph = self.loader.graph
        self.relationships = [
            item for item in graph.get("relationships", [])
            if item.get("source") in self.entities and item.get("target") in self.entities
        ]
        self.relationships.sort(key=lambda item: (item["source"], item["relationship"], item["target"]))
        self.adjacency: dict[str, list[dict[str, str]]] = {}
        self.undirected: dict[str, list[dict[str, str]]] = {}
        for edge in self.relationships:
            self.adjacency.setdefault(edge["source"], []).append(edge)
            self.undirected.setdefault(edge["source"], []).append(edge)
            self.undirected.setdefault(edge["target"], []).append({"source": edge["target"], "target": edge["source"], "relationship": edge["relationship"]})
        for mapping in (self.adjacency, self.undirected):
            for key in mapping:
                mapping[key].sort(key=lambda edge: self._edge_order(edge))
        canonical = "\n".join(f"{edge['source']}|{edge['relationship']}|{edge['target']}" for edge in self.relationships)
        self.graph_version = sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def _resolve_key(self, value: str) -> str:
        if value in self.entities:
            return value
        entity = self.loader.resolve(value)
        if not entity:
            raise ValueError(f"Unknown entity: {value}")
        return f"{entity['type']}:{entity['id']}"

    def _status(self, key: str) -> str:
        return str(self.entities[key].get("verification", {}).get("status") or "unknown")

    def _edge_order(self, edge: dict[str, str]) -> tuple[int, int, str, str]:
        target = edge["target"]
        return (-RELATIONSHIP_WEIGHTS.get(edge["relationship"], 40), -CONFIDENCE_WEIGHTS.get(self._status(target), 0), edge["relationship"], target)

    def _summary(self, key: str, *, distance: int | None = None) -> dict[str, Any]:
        entity = self.entities[key]
        result = {
            "key": key,
            "id": entity["id"],
            "type": entity["type"],
            "name": entity["name"],
            "description": entity.get("description", ""),
            "category": entity.get("category", ""),
            "difficulty": entity.get("difficulty", ""),
            "verification": entity.get("verification", {}),
        }
        if distance is not None:
            result["distance"] = distance
        return result

    def _relationship_explanation(self, edge: dict[str, str]) -> dict[str, Any]:
        relationship = edge["relationship"]
        prefix = next((name for name in KNOWN_EXPLANATIONS if relationship.startswith(name)), None)
        source, target = self.entities[edge["source"]]["name"], self.entities[edge["target"]]["name"]
        if prefix:
            level = relationship.rsplit("-", 1)[-1] if relationship.startswith("requires-prerequisite-") else "published"
            why = KNOWN_EXPLANATIONS[prefix].format(source=source, target=target, level=level)
            evidence = "generated authored relationship metadata"
        else:
            why = "Explanation unavailable; relationship requires human review."
            evidence = "no controlled explanation template"
        confidence = min(CONFIDENCE_WEIGHTS.get(self._status(edge["source"]), 0), CONFIDENCE_WEIGHTS.get(self._status(edge["target"]), 0))
        label = {4: "high", 3: "medium", 2: "needs-review", 1: "unknown", 0: "unknown"}[confidence]
        return {"source": edge["source"], "target": edge["target"], "relationship_type": relationship, "why": why, "evidence": evidence, "confidence": label}

    def metadata(self) -> dict[str, Any]:
        return {"knowledge_version": self._knowledge_version(), "graph_version": self.graph_version, "generated_at": self.loader.health.get("as_of", "controlled-repository-artifact"), "node_count": len(self.entities), "edge_count": len(self.relationships)}

    def relationship_types(self) -> set[str]:
        return {edge["relationship"] for edge in self.relationships}

    def _knowledge_version(self) -> str:
        payload = "\n".join(sorted(self.entities))
        return sha256(payload.encode("utf-8")).hexdigest()[:16]

    def neighborhood(self, entity: str, *, depth: int = 1, node_limit: int = 100, edge_limit: int = 200, entity_types: set[str] | None = None, relationship_types: set[str] | None = None, trust_statuses: set[str] | None = None) -> dict[str, Any]:
        if not 1 <= depth <= MAX_DEPTH or not 1 <= node_limit <= MAX_NODES or not 1 <= edge_limit <= MAX_EDGES:
            raise ValueError("graph traversal limit is outside the supported range")
        root = self._resolve_key(entity)
        selected, distances = {root}, {root: 0}
        queue = deque([root])
        edges: list[dict[str, Any]] = []
        truncated = False
        while queue:
            current = queue.popleft()
            if distances[current] >= depth:
                continue
            for edge in self.adjacency.get(current, []):
                target = edge["target"]
                if relationship_types and edge["relationship"] not in relationship_types:
                    continue
                if entity_types and self.entities[target]["type"] not in entity_types:
                    continue
                if trust_statuses and self._status(target) not in trust_statuses:
                    continue
                if target not in selected:
                    if len(selected) >= node_limit:
                        truncated = True
                        continue
                    selected.add(target)
                    distances[target] = distances[current] + 1
                    queue.append(target)
                if len(edges) >= edge_limit:
                    truncated = True
                    continue
                if target in selected:
                    edges.append({**edge, "explanation": self._relationship_explanation(edge)})
        nodes = [self._summary(key, distance=distances.get(key, 0)) for key in sorted(selected, key=lambda key: (distances.get(key, 0), key))]
        return {**self.metadata(), "center": self._summary(root, distance=0), "nodes": nodes, "relationships": edges, "depth": depth, "limit": node_limit, "edge_limit": edge_limit, "truncated": truncated}

    def path(self, start: str, end: str, *, max_length: int = MAX_PATH_LENGTH) -> dict[str, Any]:
        if not 1 <= max_length <= MAX_PATH_LENGTH:
            raise ValueError("maximum path length is outside the supported range")
        source, target = self._resolve_key(start), self._resolve_key(end)
        if source == target:
            return {**self.metadata(), "from": source, "to": target, "found": True, "path": [self._summary(source)], "relationships": []}
        queue, previous = deque([source]), {source: None}
        previous_edge: dict[str, dict[str, str]] = {}
        while queue:
            current = queue.popleft()
            current_length = sum(1 for _ in self._walk_previous(previous, current)) - 1
            if current_length >= max_length:
                continue
            for edge in self.adjacency.get(current, []):
                neighbor = edge["target"]
                if neighbor in previous:
                    continue
                previous[neighbor], previous_edge[neighbor] = current, edge
                if neighbor == target:
                    queue.clear()
                    break
                queue.append(neighbor)
        if target not in previous:
            return {**self.metadata(), "from": source, "to": target, "found": False, "path": [], "relationships": []}
        keys = list(reversed(list(self._walk_previous(previous, target))))
        edges = [self._relationship_explanation(previous_edge[key]) for key in keys[1:]]
        return {**self.metadata(), "from": source, "to": target, "found": True, "path": [self._summary(key) for key in keys], "relationships": edges}

    @staticmethod
    def _walk_previous(previous: dict[str, str | None], cursor: str):
        while cursor is not None:
            yield cursor
            cursor = previous[cursor]

    def prerequisites(self, entity: str, *, completed: set[str] | None = None) -> dict[str, Any]:
        root, completed = self._resolve_key(entity), completed or set()
        groups: dict[str, list[dict[str, Any]]] = {"required": [], "recommended": [], "helpful": []}
        for edge in self.adjacency.get(root, []):
            prefix = "requires-prerequisite-"
            if not edge["relationship"].startswith(prefix):
                continue
            level = edge["relationship"][len(prefix):]
            if level not in groups:
                continue
            item = self._summary(edge["target"])
            item["completed"] = edge["target"] in completed
            item["explanation"] = self._relationship_explanation(edge)
            groups[level].append(item)
        missing = [item for group in groups.values() for item in group if not item["completed"]]
        return {**self.metadata(), "entity": self._summary(root), **groups, "completed": [item for group in groups.values() for item in group if item["completed"]], "missing": missing}

    def learning_route(self, entity: str, *, completed: set[str] | None = None, include_completed: bool = False) -> dict[str, Any]:
        root, completed = self._resolve_key(entity), completed or set()
        ordered: list[tuple[str, dict[str, str] | None]] = []
        visited: set[str] = set()
        visiting: set[str] = set()

        def visit(key: str, edge: dict[str, str] | None = None) -> None:
            if key in visited or key in visiting:
                return
            visiting.add(key)
            prerequisites = [item for item in self.adjacency.get(key, []) if item["relationship"].startswith("requires-prerequisite-")]
            for prerequisite in prerequisites:
                visit(prerequisite["target"], prerequisite)
            visiting.remove(key)
            visited.add(key)
            if include_completed or key not in completed:
                ordered.append((key, edge))

        visit(root)
        steps = []
        for index, (key, edge) in enumerate(ordered, start=1):
            step = self._summary(key)
            step["order"] = index
            step["completed"] = key in completed
            step["why"] = self._relationship_explanation(edge)["why"] if edge else "This is the selected generated knowledge entity."
            steps.append(step)
        return {**self.metadata(), "entity": self._summary(root), "steps": steps, "completed_omitted": len(visited) - len(steps)}

    def impact(self, entity: str, *, depth: int = 1, node_limit: int = MAX_NODES) -> dict[str, Any]:
        if not 1 <= depth <= MAX_DEPTH or not 1 <= node_limit <= MAX_NODES:
            raise ValueError("graph traversal limit is outside the supported range")
        root, selected, distances = self._resolve_key(entity), set(), {}
        queue = deque([(root, 0)])
        truncated = False
        while queue:
            current, distance = queue.popleft()
            if distance >= depth:
                continue
            for edge in self.undirected.get(current, []):
                target = edge["target"]
                if target == root or target in selected:
                    continue
                if len(selected) >= node_limit:
                    truncated = True
                    continue
                selected.add(target); distances[target] = distance + 1; queue.append((target, distance + 1))
        grouped: dict[str, list[dict[str, Any]]] = {kind: [] for kind in sorted({item["type"] for item in self.entities.values()})}
        for key in sorted(selected, key=lambda key: (self.entities[key]["type"], key)):
            grouped[self.entities[key]["type"]].append(self._summary(key, distance=distances[key]))
        return {**self.metadata(), "entity": self._summary(root), "depth": depth, "truncated": truncated, "affected": grouped}

    def attack_defense(self, entity: str) -> dict[str, Any]:
        root = self._resolve_key(entity)
        neighborhood = self.neighborhood(root, depth=2, node_limit=100, edge_limit=200)
        sections: dict[str, list[dict[str, Any]]] = {"techniques": [], "vulnerabilities": [], "detection": [], "defensive_controls": [], "mitigations": [], "labs": []}
        seen: set[tuple[str, str]] = set()
        for node in neighborhood["nodes"]:
            if node["key"] == root:
                continue
            key = (node["type"], node["id"])
            if key in seen:
                continue
            seen.add(key)
            if node["type"] == "technique": sections["techniques"].append(node)
            elif node["type"] == "vulnerability": sections["vulnerabilities"].append(node)
            elif node["type"] == "defensive-control": sections["defensive_controls"].append(node)
            elif node["type"] == "lab": sections["labs"].append(node)
        for edge in neighborhood["relationships"]:
            relationship = edge["relationship"]
            target = self._summary(edge["target"])
            if "detect" in relationship:
                sections["detection"].append(target)
            if relationship in {"mitigated-by", "control-for"}:
                sections["mitigations"].append(target)
        for name in sections:
            unique = {item["key"]: item for item in sections[name]}
            sections[name] = [unique[key] for key in sorted(unique)]
        return {**self.metadata(), "entity": self._summary(root), **sections}

    def graph_search(self, query: str, *, limit: int = 20, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        if not 1 <= limit <= 100:
            raise ValueError("search limit is outside the supported range")
        direct = SearchEngine(self.loader).search(query, limit=100, **(filters or {}))["results"]
        direct_keys = {f"{item['type']}:{item['id']}" for item in direct}
        results = [{**item, "match_type": "direct", "graph_reason": "Direct deterministic keyword match."} for item in direct[:limit]]
        inferred: dict[str, dict[str, Any]] = {}
        for source in direct[:10]:
            source_key = f"{source['type']}:{source['id']}"
            for edge in self.adjacency.get(source_key, []):
                target = edge["target"]
                if target in direct_keys or target in inferred:
                    continue
                item = self._summary(target)
                inferred[target] = {**item, "score": max(0, int(source["score"]) - 1), "reasons": ["graph relationship"], "match_type": "related", "graph_reason": f"Related to direct match {source['name']} through {edge['relationship']}."}
        for key in sorted(inferred, key=lambda key: (-inferred[key]["score"], key)):
            if len(results) >= limit:
                break
            results.append(inferred[key])
        return {**self.metadata(), "query": query, "total": len(results), "results": results, "ranking": {"algorithm": "deterministic-direct-then-graph"}}

    def orphan_suggestions(self, *, limit: int = 100) -> dict[str, Any]:
        if not 1 <= limit <= MAX_NODES:
            raise ValueError("suggestion limit is outside the supported range")
        degree = {key: len(self.undirected.get(key, [])) for key in self.entities}
        orphans = [key for key in sorted(self.entities) if degree[key] == 0]
        rows = []
        for orphan in orphans[:limit]:
            source = self.entities[orphan]
            candidates: list[tuple[int, str, list[str]]] = []
            source_tokens = token_set([source.get("category", ""), source.get("tags", []), source.get("platforms", []), source.get("security_domains", [])])
            for key, target in self.entities.items():
                if key == orphan or degree[key] == 0:
                    continue
                overlap = source_tokens.intersection(token_set([target.get("category", ""), target.get("tags", []), target.get("platforms", []), target.get("security_domains", [])]))
                if not overlap:
                    continue
                candidates.append((len(overlap), key, sorted(overlap)))
            candidates.sort(key=lambda item: (-item[0], item[1]))
            rows.append({"entity": self._summary(orphan), "reason": "No generated graph relationships reference this entity.", "existing_relationships": [], "suggestions": [{"entity": self._summary(key), "shared_metadata": shared, "status": "SUGGESTION ONLY — REQUIRES HUMAN REVIEW"} for _, key, shared in candidates[:5]]})
        return {**self.metadata(), "total": len(orphans), "items": rows, "limit": limit}
