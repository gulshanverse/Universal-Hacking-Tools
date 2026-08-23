from ..indexes.index_loader import IndexLoader


class HealthEngine:
    def __init__(self, loader=None):
        self.loader = loader or IndexLoader()

    def report(self):
        return self.loader.health

    def score(self):
        return self.loader.health.get("overall_score", 0)

    def stale(self):
        return self.loader.health.get("stale_verification", [])

    def orphans(self):
        return self.loader.health.get("orphaned_entities", [])
