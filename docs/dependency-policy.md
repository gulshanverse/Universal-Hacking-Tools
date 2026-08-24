# Dependency and Supply-Chain Policy

Python requirements and the web `pnpm-lock.yaml` are versioned alongside the application. Dependency changes must be intentional, reviewed, and validated; Phase 11 does not blindly upgrade packages.

| Area | Policy |
| --- | --- |
| Python | Review known security advisories and compatibility before changing pinned or constrained requirements. Run syntax, API, migration, and artifact checks after updates. |
| Node/pnpm | Preserve the lockfile, use frozen installs in CI, run static tests, type checks, and explicit production build. |
| GitHub Actions | Use reviewed official actions with least `contents: read` permission by default. Do not expose deployment secrets to forked pull requests. |
| Abandoned dependencies | Evaluate maintenance, release history, security advisories, and replacement impact before adoption or removal. |
| Containers | No production container image is defined by this repository. If one is introduced, pin its base image and scan it in the selected provider workflow. |

During Phase 11 local validation, `pip-audit -r apps/api/requirements.txt` and `pnpm audit --prod --audit-level=high` reported no known vulnerabilities after the web lockfile was resolved with workspace-level PostCSS `8.5.26` and sharp `0.35.0` overrides. The initial web audit had identified vulnerable transitive copies from the existing Next.js chain; the override is intentionally narrow and the full static/type/build suite is required after every lockfile change. The official [July 2026 Next.js security release](https://nextjs.org/blog/july-2026-security-release) confirms that maintained 15.5 releases receive security patches; the project remains on its existing 15.5 line rather than performing an unreviewed framework major upgrade.

Routine dependency review cadence and external vulnerability-scanner configuration are **not-configured** until the deployment/organization tooling is selected. The local and CI dependency audit results must be recorded as evidence rather than inferred from this policy.
