# Search, Discovery, and Knowledge Intelligence

Phase 3 adds an **offline deterministic intelligence layer** over the repository’s Markdown + YAML source and generated JSON artifacts. It does not add a database, web server, frontend, external search API, telemetry, LLM, embeddings, or network dependency.

## Architecture

```text
Markdown + YAML
      ↓
Phase 1/2 validation and graph generation
      ↓
Normalized generated JSON
      ↓
Search index, aliases, and health report
      ↓
SearchEngine / DiscoveryEngine / RecommendationEngine / ComparisonEngine / HealthEngine
      ↓
CLI now; future API or website later
```

The [`IndexLoader`](indexes/index_loader.py) reads only committed local JSON. Engines are separated from the CLI so a future API can reuse the same interfaces without parsing Markdown.

## Search Model

[`generated/search-index.json`](../generated/search-index.json) stores one compact normalized document per entity. It includes identifiers, type, name, description, category, subcategory, tags, difficulty, platforms, security domains, relationships, verification, sources, aliases, keywords, and normalized tokens. Hyphens, underscores, punctuation, case, and repeated whitespace are normalized consistently, so `OWASP ZAP`, `owasp-zap`, and `OWASP_ZAP` resolve to the same search vocabulary.

## Ranking

Ranking is transparent and deterministic. The current scoring weights are defined in [`ranking/ranker.py`](ranking/ranker.py): exact name `+100`, exact alias `+95`, name prefix `+80`, name-token match `+70`, description `+40`, category or subcategory `+30`, tag `+25`, and relationship match `+20`. Additional multi-term keyword matches contribute a small deterministic amount. Ties are resolved by entity type, display name, and ID.

## Filters

The search engine supports `type`, `category`, `subcategory`, `difficulty`, `platform`, `security_domain`, `license`, `dual_use`, and `verification_status`. Filters are applied before ranking. Multi-entity queries such as `web security`, `network scanning`, and `authentication vulnerabilities` use normalized metadata and relationship-aware keywords rather than relying only on page text.

## Aliases

[`generated/aliases.json`](../generated/aliases.json) contains a deterministic alias-to-entity map for legitimate terminology such as `SQLi`, `XSS`, `CSRF`, `RCE`, `MFA`, `IDS`, `IPS`, `ZAP`, `John`, and `OpenVAS`. Alias resolution is intentionally conservative: ambiguous aliases do not silently select an entity.

## Discovery and Paths

[`DiscoveryEngine`](engine/discovery_engine.py) provides bounded `explore(entity_id, depth)` traversal with cycle prevention and stable ordering. `find_path(start, end)` uses breadth-first search over the generated graph and returns an empty path when no route exists. Relationships are represented as typed IDs such as `tool:nmap` and `technique:network-scanning`.

## Recommendations

[`RecommendationEngine`](engine/recommendation_engine.py) uses rules rather than AI. It prioritizes nearby concepts, techniques, safe labs, tools, and defensive controls according to graph distance, learner level, goal terms, and accessible progression. It does not execute tools or recommend unauthorized offensive activity.

## Tool Comparison

[`ComparisonEngine`](engine/comparison_engine.py) compares known metadata only: purpose, category, difficulty, platforms, license, security domains, capabilities represented by indexed keywords, limitations, relationships, labs, verification, and sources. It deliberately does not invent benchmarks or performance claims.

## Knowledge Health

[`generated/knowledge-health.json`](../generated/knowledge-health.json) records entity counts, verification statuses, missing sources or descriptions, missing relationships, orphaned entities, broken relationships, stale verification dates, duplicate aliases, duplicate names, and transparent component and overall scores. The report uses a fixed documented `as_of` date and configurable stale threshold in the generator so committed output remains deterministic.

## CLI

Examples:

```bash
python3 scripts/search.py nmap
python3 scripts/search.py "network scanning" --type tool --difficulty beginner --platform linux
python3 scripts/search.py --explore nmap --depth 2
python3 scripts/search.py --path nmap firewall
python3 scripts/search.py --compare nmap masscan
python3 scripts/search.py --recommend nmap --difficulty beginner --goals network-security
python3 scripts/search.py --health
```

Pass `--format json` for stable machine-readable output. The CLI treats repository content as data and never executes commands, performs scans, makes external requests, or evaluates user input as code.

## Regeneration

Run `python3 scripts/generate-knowledge.py`, then `python3 scripts/generate-search.py`. Validation commands are documented in [`CONTRIBUTING.md`](../CONTRIBUTING.md). Generated artifacts must be current before a pull request is merged.

## Future API Integration

A future API or website can load the generated JSON through the same engine interfaces. It should not parse raw Markdown at request time. Database-backed indexing, full-text services, graph databases, frontend frameworks, and semantic or AI ranking are intentionally deferred until this deterministic baseline has been proven.
