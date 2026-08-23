#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ERRORS = []

def load(name):
    path = ROOT / 'generated' / name
    if not path.exists(): ERRORS.append(f'missing generated/{name}'); return {}
    try: return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc: ERRORS.append(f'invalid generated/{name}: {exc}'); return {}

def main():
    docs = load('search-index.json').get('documents', [])
    complete = load('content-completeness.json')
    verification = load('verification-report.json')
    queue = load('review-queue.json')
    expected = {f"{d['type']}:{d['id']}" for d in docs}
    entities = complete.get('entities', [])
    actual = {f"{e.get('type')}:{e.get('id')}" for e in entities}
    if len(actual) != len(entities): ERRORS.append('content-completeness contains duplicate typed entities')
    if actual != expected: ERRORS.append('content-completeness entity set differs from search index')
    for entity in entities:
        if not isinstance(entity.get('completeness_score'), (int, float)): ERRORS.append(f"invalid completeness score for {entity.get('id')}")
        if not isinstance(entity.get('recommended_actions'), list): ERRORS.append(f"invalid recommended actions for {entity.get('id')}")
    totals = verification.get('totals', {})
    if totals.get('total') != len(docs): ERRORS.append('verification total differs from search index')
    by_type_total = sum(item.get('total', 0) for item in verification.get('by_entity_type', {}).values())
    if by_type_total != len(docs): ERRORS.append('verification type totals do not sum to entity total')
    queue_ids = {f"{i.get('type')}:{i.get('id')}" for i in queue.get('items', [])}
    if not queue_ids.issubset(expected): ERRORS.append('review queue contains an unknown entity')
    if queue.get('total_items') != len(queue.get('items', [])): ERRORS.append('review queue count is incorrect')
    for item in queue.get('items', []):
        if not isinstance(item.get('priority'), int) or item['priority'] < 1: ERRORS.append(f"invalid review priority for {item.get('id')}")
    if ERRORS:
        print('Quality validation failed:\n' + '\n'.join('- ' + e for e in ERRORS)); return 1
    print(f"Validated completeness ({len(entities)} entities), verification totals, and review queue ({len(queue.get('items', []))} items).")
    return 0
if __name__ == '__main__': sys.exit(main())
