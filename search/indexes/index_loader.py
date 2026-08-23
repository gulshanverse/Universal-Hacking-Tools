from pathlib import Path
import json, re


def normalize(value):
    """Normalize search text while retaining meaningful security terms."""
    value = str(value or "").lower().replace("_", " ").replace("-", " ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def token_set(value):
    return set(normalize(value).split())


class IndexLoader:
    """Read deterministic generated artifacts without network or code execution."""
    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parents[2])
        self.generated = self.root / "generated"
        self._cache = {}

    def load(self, filename):
        if filename not in self._cache:
            self._cache[filename] = json.loads((self.generated / filename).read_text(encoding="utf-8"))
        return self._cache[filename]

    @property
    def documents(self):
        return self.load("search-index.json")["documents"]

    @property
    def aliases(self):
        return self.load("aliases.json").get("aliases", {})

    @property
    def graph(self):
        return self.load("knowledge-graph.json")

    @property
    def health(self):
        return self.load("knowledge-health.json")

    def entity_map(self):
        return {f"{d['type']}:{d['id']}": d for d in self.documents}

    def resolve(self, value, entity_type=None):
        """Resolve an id, typed id, name, or unambiguous alias deterministically."""
        query = normalize(value)
        docs = [d for d in self.documents if entity_type is None or d["type"] == entity_type]
        typed = query.replace(" ", ":", 1) if ":" in str(value) else ""
        if typed in {f"{d['type']}:{d['id']}" for d in docs}:
            return self.entity_map()[typed]
        for d in docs:
            if normalize(d["id"]) == query or normalize(d["name"]) == query:
                return d
        matches = []
        for alias, ids in self.aliases.items():
            if normalize(alias) == query:
                for target in ids:
                    if target in self.entity_map() and (entity_type is None or target.startswith(entity_type + ":")):
                        matches.append(self.entity_map()[target])
        if len(matches) == 1:
            return matches[0]
        return None
