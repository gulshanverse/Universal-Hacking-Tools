from collections import deque
from ..indexes.index_loader import IndexLoader


class DiscoveryEngine:
    def __init__(self, loader=None):
        self.loader = loader or IndexLoader()
        self.entities = self.loader.entity_map()
        self.adjacency = {}
        for rel in self.loader.graph.get("relationships", []):
            self.adjacency.setdefault(rel["source"], []).append((rel["target"], rel["relationship"]))
        for key in self.adjacency:
            self.adjacency[key].sort(key=lambda item: (item[0], item[1]))

    def _resolve_key(self, value):
        if ":" in str(value) and str(value) in self.entities:
            return str(value)
        entity = self.loader.resolve(value)
        if not entity:
            raise ValueError(f"Unknown entity: {value}")
        return f"{entity['type']}:{entity['id']}"

    def explore(self, entity_id, depth=1):
        depth = max(0, int(depth))
        root_key = self._resolve_key(entity_id)
        distances = {root_key: 0}
        paths = {root_key: [root_key]}
        queue = deque([root_key])
        while queue:
            current = queue.popleft()
            if distances[current] >= depth:
                continue
            for target, relationship in self.adjacency.get(current, []):
                if target not in distances:
                    distances[target] = distances[current] + 1
                    paths[target] = paths[current] + [target]
                    queue.append(target)
        related = []
        for key, distance in sorted(distances.items(), key=lambda item: (item[1], item[0])):
            if key == root_key:
                continue
            item = dict(self.entities[key])
            item["distance"] = distance
            item["path"] = paths[key]
            related.append(item)
        return {"entity": self.entities[root_key], "related": related, "paths": [paths[key] for key in sorted(paths, key=lambda k: (len(paths[k]), k)) if key != root_key]}

    def find_path(self, start, end):
        start_key, end_key = self._resolve_key(start), self._resolve_key(end)
        if start_key == end_key:
            return [start_key]
        queue = deque([start_key])
        previous = {start_key: None}
        while queue:
            current = queue.popleft()
            for target, _ in self.adjacency.get(current, []):
                if target in previous:
                    continue
                previous[target] = current
                if target == end_key:
                    queue.clear()
                    break
                queue.append(target)
        if end_key not in previous:
            return []
        path = []
        cursor = end_key
        while cursor is not None:
            path.append(cursor)
            cursor = previous[cursor]
        return list(reversed(path))
