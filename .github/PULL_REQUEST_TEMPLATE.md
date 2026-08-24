## Summary

Describe the change, its intended learner value, and whether it changes canonical Markdown/YAML knowledge, generated artifacts, application state, API contracts, or the web client.

## Sources and reviewability

List official repositories, documentation, standards, or other authoritative sources. Explain unresolved uncertainty, duplicate candidates, relationship effects, and any reviewer or maintainer decisions that need human follow-up.

## Safety, privacy, and community boundary

- [ ] Examples are limited to owned, synthetic, local, CTF, or explicitly authorized environments.
- [ ] No secrets, personal data, malware, credential theft, persistence, evasion, destructive content, target-selection fields, uploads, or arbitrary execution are included.
- [ ] Dual-use material includes detection and mitigation.
- [ ] Community proposals remain non-canonical application state; no web route directly changes Markdown/YAML, generated artifacts, labs, or Git history.
- [ ] Sensitive reports are private and are not reproduced in public issues, reviews, or this pull request.

## Validation

- [ ] `python3 scripts/validate_repository.py`
- [ ] `python3 scripts/generate-index.py --check`
- [ ] `PYTHONPATH=apps/api:. python3 -m unittest discover -s apps/api/tests -v` when API/state behavior changes
- [ ] Alembic upgrade → downgrade → upgrade exercised on a disposable database when migrations change
- [ ] `python3 apps/api/scripts/export_openapi.py` and `PYTHONPATH=apps/api:. python3 apps/api/scripts/check_openapi.py` when routes change
- [ ] `cd apps/web && pnpm test && pnpm typecheck && NODE_ENV=production pnpm build` when web code changes
