#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ERRORS=[]
VALID_STATUS={"verified","partially-verified","needs-review","unverified","deprecated"}
VALID_CONFIDENCE={"high","medium","low","unknown"}
VALID_METHOD={"official-documentation","official-repository","official-website","maintainer-documentation","security-standard","vendor-documentation","primary-research","secondary-research","manual-review","cross-source-review"}

def load(name):
    p=ROOT/'generated'/name
    if not p.exists(): ERRORS.append(f'missing generated/{name}'); return {}
    try: return json.loads(p.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e: ERRORS.append(f'invalid generated/{name}: {e}'); return {}

def main():
    search=load('search-index.json'); docs=search.get('documents',[])
    trust=load('trust-report.json'); catalog=load('source-catalog.json'); claims=load('claim-report.json'); prereq=load('prerequisite-report.json')
    expected={f"{d.get('type')}:{d.get('id')}" for d in docs}
    entities=trust.get('entity_trust',[])
    actual={e.get('entity') for e in entities}
    if actual != expected: ERRORS.append('trust entity set differs from search index')
    for d in docs:
        v=d.get('verification',{})
        if v.get('status') not in VALID_STATUS: ERRORS.append(f"invalid verification status for {d.get('id')}")
        if v.get('confidence') not in VALID_CONFIDENCE: ERRORS.append(f"invalid confidence for {d.get('id')}")
        if v.get('verification_method') not in VALID_METHOD: ERRORS.append(f"invalid verification method for {d.get('id')}")
    for e in entities:
        if not isinstance(e.get('trust_score'),(int,float)) or not 0 <= e['trust_score'] <= 100: ERRORS.append(f"invalid trust score for {e.get('entity')}")
    urls=set(); source_ids=set()
    for source in catalog.get('sources',[]):
        if not source.get('url') or not source.get('normalized_url'): ERRORS.append(f"source missing URL: {source.get('id')}")
        urls.add(source.get('normalized_url')); source_ids.add((source.get('entity'), source.get('id')))
    if catalog.get('invalid_sources'): ERRORS.append(f"source catalog contains {len(catalog['invalid_sources'])} invalid source records")
    claim_ids=set()
    for claim in claims.get('claims',[]):
        key=(claim.get('entity'),claim.get('id'))
        if key in claim_ids: ERRORS.append(f'duplicate claim: {key}')
        claim_ids.add(key)
    if claims.get('findings'): ERRORS.append(f"claim report contains {len(claims['findings'])} findings")
    overall=trust.get('overall',{}).get('trust_score')
    if not isinstance(overall,(int,float)) or not 0 <= overall <= 100: ERRORS.append('invalid overall trust score')
    if prereq.get('cycles'): ERRORS.append(f"prerequisite cycles detected: {len(prereq['cycles'])}")
    if prereq.get('invalid',0): ERRORS.append(f"invalid prerequisites detected: {prereq['invalid']}")
    if ERRORS:
        print('Trust validation failed:\n'+'\n'.join('- '+e for e in ERRORS)); return 1
    print(f"Validated verification metadata for {len(docs)} entities, {len(catalog.get('sources',[]))} normalized sources, {len(claims.get('claims',[]))} claims, and trust score {overall}%.")
    return 0
if __name__=='__main__': sys.exit(main())
