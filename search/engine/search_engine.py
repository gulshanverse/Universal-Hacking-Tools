from ..indexes.index_loader import IndexLoader, normalize, token_set
from ..ranking.ranker import score


class SearchEngine:
    """Search normalized generated JSON; never executes or fetches anything."""
    CATEGORY_ALIASES = {
        "network security": "network analysis",
        "web security": "web security",
        "cloud security": "cloud security",
        "defensive security": "defensive security",
        "secure development": "secure development",
        "container security": "container security",
    }
    def __init__(self, loader=None):
        self.loader = loader or IndexLoader()

    def _matches_filter(self, document, filters):
        for key, expected in filters.items():
            if expected in (None, "", []):
                continue
            value = document.get("platforms", []) if key == "platform" else document.get(key, "")
            if key == "type":
                value = document.get("type", "")
            if key == "verification_status":
                value = document.get("verification", {}).get("status", "")
            if key == "security_domain":
                value = document.get("security_domains", [])
            values = value if isinstance(value, list) else [value]
            actual = normalize(" ".join(str(x) for x in values))
            wanted = normalize(expected)
            if key == "category":
                requested = normalize(expected)
                wanted = normalize(self.CATEGORY_ALIASES.get(requested, requested))
                context = normalize(" ".join(str(x) for x in [document.get("category", ""), document.get("subcategory", ""), document.get("security_domains", [])]))
                if requested == "network security" and "network" in context:
                    continue
            if key == "dual_use":
                if str(value).lower() != str(expected).lower(): return False
            elif wanted not in actual:
                return False
        return True

    def _field_score(self, document, query):
        q_tokens = token_set(query)
        if not q_tokens:
            return 0, []
        fields = [document.get("name", ""), document.get("description", ""), document.get("category", ""), document.get("subcategory", ""), document.get("tags", []), document.get("keywords", [])]
        available = token_set(fields)
        hits = q_tokens.intersection(available)
        if not hits:
            return 0, []
        return len(hits) * 8, [f"keyword match ({len(hits)})"]

    def search(self, query="", limit=20, **filters):
        results = []
        for document in self.loader.documents:
            if not self._matches_filter(document, filters):
                continue
            base, reasons = score(document, query, self.loader.aliases) if query else (0, [])
            extra, extra_reasons = self._field_score(document, query)
            total = base + extra
            if query and total == 0:
                continue
            results.append({"id": document["id"], "type": document["type"], "name": document["name"], "path": document["path"], "category": document.get("category", ""), "difficulty": document.get("difficulty", ""), "score": total, "reasons": reasons + extra_reasons, "description": document.get("description", "")})
        results.sort(key=lambda x: (-x["score"], x["type"], x["name"].lower(), x["id"]))
        return {"query": query, "filters": filters, "total": len(results), "results": results[:max(0, int(limit))]}
