# Privacy Notice for Phase 8

Phase 8 stores the minimum private application state needed for an account: normalized email, password hash, session records, optional learning goals, private progress, bookmarks, plain-text private notes, minimal lab-attempt summaries, achievements, and private recommendation snapshots. The platform does not store plaintext passwords, raw session tokens, raw verification/reset tokens, raw Phase 6 local lab evidence, public profiles, comments, messages, telemetry, or third-party analytics.

Cookies are used only for secure authenticated sessions and CSRF protection. The browser does not store long-lived authentication credentials in localStorage. Private data is served only through authenticated, owner-scoped routes. Account deletion revokes sessions and deletes associated private state; public cybersecurity knowledge and public lab definitions remain in the Git-backed repository.

Sessions and temporary verification/reset records expire. Notes are retained until their owner deletes them or deletes the account. Lab attempt summaries are retained only until account deletion. This document describes engineering intent and does not claim legal certification or regulatory compliance.
