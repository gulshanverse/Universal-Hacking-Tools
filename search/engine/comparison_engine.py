from ..indexes.index_loader import IndexLoader


class ComparisonEngine:
    def __init__(self, loader=None):
        self.loader = loader or IndexLoader()

    def _tool(self, value):
        tool = self.loader.resolve(value, entity_type="tool")
        if not tool:
            raise ValueError(f"Unknown tool: {value}")
        return tool

    def compare(self, tool_a, tool_b):
        a, b = self._tool(tool_a), self._tool(tool_b)
        attrs = ["name", "category", "subcategory", "difficulty", "platforms", "license", "security_domains", "dual_use", "description", "verification", "sources"]
        comparison = {attribute: {"a": a.get(attribute, ""), "b": b.get(attribute, "")} for attribute in attrs}
        comparison["capabilities"] = {"a": sorted(a.get("keywords", [])), "b": sorted(b.get("keywords", []))}
        comparison["limitations"] = {"a": "See the tool page for documented limitations.", "b": "See the tool page for documented limitations."}
        comparison["related_techniques"] = {"a": sorted(r["target"] for r in a.get("relationships", []) if r["target"].startswith("technique:")), "b": sorted(r["target"] for r in b.get("relationships", []) if r["target"].startswith("technique:"))}
        comparison["related_technologies"] = {"a": sorted(r["target"] for r in a.get("relationships", []) if r["target"].startswith("technology:")), "b": sorted(r["target"] for r in b.get("relationships", []) if r["target"].startswith("technology:"))}
        comparison["labs"] = {"a": sorted(r["target"] for r in a.get("relationships", []) if r["target"].startswith("lab:")), "b": sorted(r["target"] for r in b.get("relationships", []) if r["target"].startswith("lab:"))}
        return {"tool_a": a, "tool_b": b, "comparison": comparison, "benchmarking": "Not provided; compare performance only in a representative authorized lab."}
