"""Immutable generated-contract access for the Phase 7 API.

The service never parses Markdown, invokes generators, or contacts the network.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from typing import Any
import json

from search.indexes.index_loader import IndexLoader, normalize
from search.engine.search_engine import SearchEngine
from search.engine.discovery_engine import DiscoveryEngine
from search.engine.recommendation_engine import RecommendationEngine
from search.engine.comparison_engine import ComparisonEngine
from search.engine.health_engine import HealthEngine
from search.graph import GraphIntelligence
from labs.engine.definition import load_definition


ROOT = Path(__file__).resolve().parents[4]
GENERATED = ROOT / "generated"
ENTITY_TYPES = {"tool", "vulnerability", "concept", "technique", "technology", "defensive-control", "lab", "learning-path"}


class ArtifactNotReady(RuntimeError):
    pass


class ArtifactService:
    required = (
        "search-index.json", "knowledge-graph.json", "knowledge-health.json", "trust-report.json",
        "review-queue.json", "lab-catalog.json", "lab-health.json", "lab-report.json", "graph-health.json",
    )

    def __init__(self, root: Path | None = None):
        self.root = Path(root or ROOT)
        self.generated = self.root / "generated"
        self._fingerprint = ""
        self._loader: IndexLoader | None = None
        self._engines: dict[str, Any] = {}
        self._json_cache: dict[str, Any] = {}

    def _current_fingerprint(self) -> str:
        if not all((self.generated / name).exists() for name in self.required):
            return "missing"
        digest = sha256()
        for name in self.required:
            digest.update(name.encode("utf-8"))
            digest.update((self.generated / name).read_bytes())
        return digest.hexdigest()[:16]

    def ready(self) -> tuple[bool, list[str]]:
        missing: list[str] = []
        for name in self.required:
            path = self.generated / name
            if not path.exists():
                missing.append(name)
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                missing.append(name)
        return not missing, missing

    def ensure_ready(self) -> None:
        ok, problems = self.ready()
        if not ok:
            raise ArtifactNotReady("required generated artifacts are unavailable: " + ", ".join(problems))
        fingerprint = self._current_fingerprint()
        if fingerprint != self._fingerprint:
            self._fingerprint = fingerprint
            self._loader = IndexLoader(self.root)
            self._engines = {}
            self._json_cache = {}

    @property
    def loader(self) -> IndexLoader:
        self.ensure_ready()
        assert self._loader is not None
        return self._loader

    def json(self, name: str) -> Any:
        self.ensure_ready()
        if name not in self._json_cache:
            self._json_cache[name] = json.loads((self.generated / name).read_text(encoding="utf-8"))
        return self._json_cache[name]

    def engine(self, name: str) -> Any:
        self.ensure_ready()
        if name not in self._engines:
            factories = {
                "search": SearchEngine,
                "discovery": DiscoveryEngine,
                "recommendation": RecommendationEngine,
                "comparison": ComparisonEngine,
                "health": HealthEngine,
                "graph": GraphIntelligence,
            }
            self._engines[name] = factories[name](self.loader)
        return self._engines[name]

    def version(self) -> str:
        self.ensure_ready()
        return self._fingerprint

    def generated_at(self) -> str:
        graph = self.json("knowledge-graph.json")
        return graph.get("generated_at") or graph.get("as_of") or "controlled-repository-artifact"

    def documents(self) -> list[dict[str, Any]]:
        return self.loader.documents

    def resolve(self, value: str, entity_type: str | None = None) -> dict[str, Any] | None:
        return self.loader.resolve(value, entity_type)

    def list_entities(self, *, entity_type: str | None = None, filters: dict[str, str | None] | None = None) -> list[dict[str, Any]]:
        filters = filters or {}
        result: list[dict[str, Any]] = []
        for document in self.documents():
            if entity_type and document.get("type") != entity_type:
                continue
            if not self._matches(document, filters):
                continue
            result.append(document)
        return sorted(result, key=lambda item: (item.get("name", "").lower(), item.get("id", "")))

    def _matches(self, document: dict[str, Any], filters: dict[str, str | None]) -> bool:
        for key, expected in filters.items():
            if expected in (None, ""):
                continue
            if key == "verification_status":
                actual = document.get("verification", {}).get("status", "")
            elif key == "confidence":
                actual = document.get("verification", {}).get("confidence", "")
            elif key == "platform":
                actual = document.get("platforms", [])
            elif key == "security_domain":
                actual = document.get("security_domains", [])
            else:
                actual = document.get(key, "")
            values = actual if isinstance(actual, list) else [actual]
            if normalize(expected) not in normalize(" ".join(str(item) for item in values)):
                return False
        return True

    def search(self, query: str, limit: int, offset: int, filters: dict[str, str | None]) -> dict[str, Any]:
        engine_filters = {key: value for key, value in filters.items() if key not in {"confidence"} and value not in (None, "")}
        raw = self.engine("search").search(query, limit=1000, **engine_filters)
        docs = {f"{item['type']}:{item['id']}": item for item in self.documents()}
        filtered = []
        for item in raw["results"]:
            document = docs.get(f"{item['type']}:{item['id']}", {})
            if self._matches(document, {"confidence": filters.get("confidence")}):
                filtered.append(item)
        return {
            "query": query,
            "total": len(filtered),
            "results": filtered[offset:offset + limit],
            "filters": {key: value for key, value in filters.items() if value not in (None, "")},
            "ranking": {"algorithm": "deterministic"},
        }

    def related(self, entity_id: str, depth: int, limit: int, relationship_type: str | None, entity_type: str | None) -> dict[str, Any]:
        result = self.engine("discovery").explore(entity_id, depth=depth)
        relationship_map = {(item["source"], item["target"]): item["relationship"] for item in self.loader.graph.get("relationships", [])}
        filtered = []
        for item in result["related"]:
            if entity_type and item.get("type") != entity_type:
                continue
            path = item.get("path", [])
            relation = relationship_map.get((path[-2], path[-1])) if len(path) >= 2 else None
            if relationship_type and relation != relationship_type:
                continue
            item = dict(item)
            item["relationship"] = relation
            filtered.append(item)
        return {"entity": result["entity"], "related": filtered[:limit], "paths": result["paths"][:limit]}

    def graph_metadata(self) -> dict[str, Any]:
        return self.engine("graph").metadata()

    def graph_export(self, entity_id: str, depth: int, node_limit: int, edge_limit: int) -> dict[str, Any]:
        result = self.engine("graph").neighborhood(entity_id, depth=depth, node_limit=node_limit, edge_limit=edge_limit)
        return {key: result[key] for key in ("knowledge_version", "graph_version", "generated_at", "nodes", "relationships", "truncated", "limit", "edge_limit")}

    def labs(self) -> list[dict[str, Any]]:
        return self.json("lab-catalog.json").get("labs", [])

    def lab(self, lab_id: str) -> dict[str, Any] | None:
        item = next((item for item in self.labs() if item.get("id") == lab_id), None)
        if not item:
            return None
        result = dict(item)
        if result.get("execution_mode") == "executable" and result.get("safety_valid"):
            definition = load_definition(lab_id)
            for field in ("objectives", "prerequisites", "tasks", "evidence", "safety", "environment", "cleanup", "learning"):
                result[field] = definition.get(field)
            result["assessment"] = definition.get("assessment")
            result["definition"] = definition.get("_path")
        return result


artifacts = ArtifactService()
