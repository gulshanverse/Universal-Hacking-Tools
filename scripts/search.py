#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from search import SearchEngine, DiscoveryEngine, RecommendationEngine, ComparisonEngine, HealthEngine


def parser():
    p = argparse.ArgumentParser(description="Search and explore the local Universal Hacking Tools knowledge base.")
    p.add_argument("query", nargs="*", help="search terms")
    p.add_argument("--type", dest="entity_type")
    p.add_argument("--category")
    p.add_argument("--subcategory")
    p.add_argument("--difficulty")
    p.add_argument("--platform")
    p.add_argument("--security-domain", dest="security_domain")
    p.add_argument("--license")
    p.add_argument("--dual-use", dest="dual_use")
    p.add_argument("--verification-status", dest="verification_status")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--depth", type=int, default=1)
    p.add_argument("--explore")
    p.add_argument("--path", nargs=2, metavar=("START", "END"))
    p.add_argument("--compare", nargs=2, metavar=("TOOL_A", "TOOL_B"))
    p.add_argument("--recommend")
    p.add_argument("--goals", nargs="*", default=[])
    p.add_argument("--health", action="store_true")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def execute(args):
    if args.health:
        return HealthEngine().report()
    if args.explore:
        return DiscoveryEngine().explore(args.explore, args.depth)
    if args.path:
        return {"start": args.path[0], "end": args.path[1], "path": DiscoveryEngine().find_path(*args.path)}
    if args.compare:
        return ComparisonEngine().compare(*args.compare)
    if args.recommend:
        return RecommendationEngine().recommend_next(args.recommend, args.difficulty or "beginner", args.goals, args.limit)
    query = " ".join(args.query)
    filters = {key: value for key, value in {"type": args.entity_type, "category": args.category, "subcategory": args.subcategory, "difficulty": args.difficulty, "platform": args.platform, "security_domain": args.security_domain, "license": args.license, "dual_use": args.dual_use, "verification_status": args.verification_status}.items() if value}
    return SearchEngine().search(query, args.limit, **filters)


def text_output(result):
    if "results" in result:
        print(f"{result['total']} result(s) for {result['query']!r}")
        for item in result["results"]:
            print(f"{item['score']:>3}  {item['type']:<18} {item['name']}  ({item['path']})")
            if item.get("description"): print(f"     {item['description']}")
    elif "related" in result:
        print(f"{result['entity']['name']} — {len(result['related'])} related entities")
        for item in result["related"]: print(f"{item['distance']}  {item['type']:<18} {item['name']}  ({item['path']})")
    elif "path" in result:
        print(" → ".join(result["path"]) if result["path"] else "No path found.")
    elif "recommendations" in result:
        print(f"Next steps for {result['current']['name']}")
        for item in result["recommendations"]: print(f"{item['score']:>3}  {item['type']:<18} {item['name']}")
    elif "comparison" in result:
        print(f"{result['tool_a']['name']} vs {result['tool_b']['name']}")
        for key, value in result["comparison"].items(): print(f"{key}: {value}")
    elif "overall_score" in result:
        print(f"Knowledge health: {result['overall_score']}% ({result['total_entities']} entities)")
        for key in ["missing_sources", "missing_relationships", "orphaned_entities", "stale_verification", "duplicate_aliases"]:
            print(f"{key}: {len(result.get(key, []))}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = execute(args)
    except (ValueError, KeyError) as exc:
        parser().error(str(exc))
    if args.format == "json": print(json.dumps(result, indent=2, sort_keys=True))
    else: text_output(result)
    return 0

if __name__ == "__main__": raise SystemExit(main())
