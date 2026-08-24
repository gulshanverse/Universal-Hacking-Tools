from ..indexes.index_loader import IndexLoader
from ..graph import GraphIntelligence


class ComparisonEngine:
    def __init__(self, loader=None):
        self.loader = loader or IndexLoader()
        self.graph = GraphIntelligence(self.loader)

    def _tool(self, value):
        tool = self.loader.resolve(value, entity_type="tool")
        if not tool:
            raise ValueError(f"Unknown tool: {value}")
        return tool

    def compare(self, tool_a, tool_b):
        a, b = self._tool(tool_a), self._tool(tool_b)
        a_key, b_key = f"tool:{a['id']}", f"tool:{b['id']}"
        attrs = ["name", "category", "subcategory", "difficulty", "platforms", "license", "security_domains", "dual_use", "description", "verification", "sources"]
        comparison = {attribute: {"a": a.get(attribute, ""), "b": b.get(attribute, "")} for attribute in attrs}
        comparison["capabilities"] = {"a": sorted(a.get("keywords", [])), "b": sorted(b.get("keywords", []))}
        comparison["limitations"] = {"a": "See the tool page for documented limitations.", "b": "See the tool page for documented limitations."}
        comparison["related_techniques"] = {"a": sorted(r["target"] for r in a.get("relationships", []) if r["target"].startswith("technique:")), "b": sorted(r["target"] for r in b.get("relationships", []) if r["target"].startswith("technique:"))}
        comparison["related_technologies"] = {"a": sorted(r["target"] for r in a.get("relationships", []) if r["target"].startswith("technology:")), "b": sorted(r["target"] for r in b.get("relationships", []) if r["target"].startswith("technology:"))}
        comparison["labs"] = {"a": sorted(r["target"] for r in a.get("relationships", []) if r["target"].startswith("lab:")), "b": sorted(r["target"] for r in b.get("relationships", []) if r["target"].startswith("lab:"))}
        a_targets = {edge["target"] for edge in self.graph.adjacency.get(a_key, [])}
        b_targets = {edge["target"] for edge in self.graph.adjacency.get(b_key, [])}
        common = sorted(a_targets.intersection(b_targets))
        comparison["graph_relationships"] = {
            "common": common,
            "only_a": sorted(a_targets - b_targets),
            "only_b": sorted(b_targets - a_targets),
            "explanation": "Relationship overlap is computed from published generated graph edges; it is not a performance comparison.",
        }
        return {"tool_a": a, "tool_b": b, "comparison": comparison, "benchmarking": "Not provided; compare performance only in a representative authorized lab."}
