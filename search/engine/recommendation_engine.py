from ..indexes.index_loader import IndexLoader, normalize
from .discovery_engine import DiscoveryEngine


class RecommendationEngine:
    """Rule-based next-step recommendations; no AI, network, or code execution."""
    LEVELS = {"beginner": 0, "intermediate": 1, "advanced": 2}
    TYPE_PRIORITY = {"concept": 50, "technique": 45, "lab": 40, "tool": 35, "defensive-control": 30, "technology": 25, "vulnerability": 20, "learning-path": 15}

    def __init__(self, loader=None):
        self.loader = loader or IndexLoader()
        self.discovery = DiscoveryEngine(self.loader)
        self.entities = self.loader.entity_map()

    def recommend_next(self, entity_id, difficulty="beginner", goals=None, limit=10):
        current_key = self.discovery._resolve_key(entity_id)
        current = self.entities[current_key]
        level = normalize(difficulty) or "beginner"
        goals = [normalize(goals)] if isinstance(goals, str) else [normalize(g) for g in (goals or [])]
        neighbors = self.discovery.explore(current_key, depth=2)["related"]
        results = []
        current_tokens = set(normalize(current.get("name", "")).split())
        for item in neighbors:
            key = f"{item['type']}:{item['id']}"
            if item["type"] == "learning-path" and level == "advanced":
                continue
            score = max(1, 60 - item["distance"] * 12) + self.TYPE_PRIORITY.get(item["type"], 10)
            reasons = [f"graph distance {item['distance']}"]
            item_level = normalize(item.get("difficulty", ""))
            if item_level and item_level == level:
                score += 20; reasons.append(f"{level} level")
            if item_level and level in self.LEVELS and item_level in self.LEVELS and self.LEVELS[item_level] <= self.LEVELS[level]:
                score += 8; reasons.append("accessible progression")
            item_tokens = set(normalize(" ".join(str(item.get(k, "")) for k in ["name", "category", "description"])).split())
            if current_tokens.intersection(item_tokens):
                score += 5; reasons.append("shared terminology")
            if goals and any(g in normalize(" ".join(str(item.get(k, "")) for k in ["name", "category", "description", "path"])) for g in goals):
                score += 25; reasons.append("goal match")
            results.append({"id": item["id"], "type": item["type"], "name": item["name"], "path": item["path"], "score": score, "reasons": reasons})
        results.sort(key=lambda x: (-x["score"], x["type"], x["name"].lower(), x["id"]))
        return {"current": current, "difficulty": level, "goals": goals, "prerequisites": [], "recommendations": results[:max(0, int(limit))]}

    def recommend(self, entity_id, difficulty="beginner", goals=None, limit=10):
        return self.recommend_next(entity_id, difficulty, goals, limit)
