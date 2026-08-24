# Production Observability

The application emits minimal structured API logs to its process output. This is a repository-configured control, not evidence of a hosted log sink, dashboard, alert policy, uptime monitor, or production traffic measurement.

## Structured request event

Each completed API request records an ISO-8601 UTC timestamp, level, `service=api`, event name, request correlation ID, route path, HTTP method, response status, duration in milliseconds, and selected environment. A caller may supply a syntactically constrained request ID; it is a correlation value only and is never an authentication identifier.

The logger must not record passwords, opaque session values, CSRF values, reset/verification tokens, database URLs, Git-provider credentials, request bodies, private notes, report content, raw lab evidence, or user-behavior telemetry. Error responses remain generic; exception details are not returned to clients.

## Minimum useful signals

The service exposes liveness, generated-artifact readiness, private database availability, request status, and request duration. Aggregate 4xx/5xx, latency, database connection failures, migration-preflight failures, and optional-provider failures may be derived by a selected deployment platform only after its privacy and retention policy is reviewed. The application deliberately does not collect precise location, browser fingerprinting, keystrokes, session replay, or page-by-page tracking.

## External blocker

Log destination, access controls, retention, redaction verification, dashboards, alert thresholds, and incident paging are **blocked — external prerequisites unavailable**. Before public launch, the deployment operator must configure minimal privacy-safe retention and alert ownership, then record environment-specific verification without placing secrets or private payloads in monitoring tools.
