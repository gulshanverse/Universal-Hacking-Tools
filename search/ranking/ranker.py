from ..indexes.index_loader import normalize, token_set

# Scores are intentionally explicit and documented in search/README.md.
WEIGHTS = {
    "exact_name": 100,
    "exact_alias": 95,
    "name_prefix": 80,
    "name_token": 70,
    "description": 40,
    "category": 30,
    "tag": 25,
    "relationship": 20,
}


def score(document, query, aliases=None):
    q = normalize(query)
    if not q:
        return 0, []
    name = normalize(document.get("name"))
    alias_values = [normalize(a) for a in document.get("aliases", [])]
    q_tokens = token_set(q)
    score_value, reasons = 0, []
    if q == name:
        score_value += WEIGHTS["exact_name"]; reasons.append("exact name")
    elif q in alias_values:
        score_value += WEIGHTS["exact_alias"]; reasons.append("exact alias")
    elif name.startswith(q):
        score_value += WEIGHTS["name_prefix"]; reasons.append("name prefix")
    elif q_tokens and q_tokens.issubset(token_set(name)):
        score_value += WEIGHTS["name_token"]; reasons.append("name token")
    description = normalize(document.get("description"))
    if q in description:
        score_value += WEIGHTS["description"]; reasons.append("description")
    if q in normalize(document.get("category")) or q in normalize(document.get("subcategory")):
        score_value += WEIGHTS["category"]; reasons.append("category")
    if q_tokens.intersection(token_set(document.get("tags", []))):
        score_value += WEIGHTS["tag"]; reasons.append("tag")
    relation_text = normalize(" ".join(r.get("target", "") for r in document.get("relationships", [])))
    if q_tokens.intersection(token_set(relation_text)):
        score_value += WEIGHTS["relationship"]; reasons.append("relationship")
    return score_value, reasons
