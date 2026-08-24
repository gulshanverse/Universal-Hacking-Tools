# Phase 8 Authentication and Session Model

Phase 8 uses opaque, server-side sessions. The browser receives an HttpOnly cookie containing a random session token; PostgreSQL retains only a hash of that token plus expiry, activity, and revocation state. Tokens are never returned in JSON responses, placed in URLs, stored in localStorage, or written to application logs.

Registration normalizes and validates email, enforces the password policy, creates a pending-verification account, and emits an injectable verification message without automatically trusting the account. Login uses a generic failure response to reduce enumeration, rotates session state on success, and records only safe timestamps. Verification and password-reset tokens are single-use, short-lived, random values stored as hashes.

Unsafe cookie-auth requests require the double-submit CSRF header and same-origin validation. Cookies are `HttpOnly`, `SameSite=Lax`, scoped to the API path, and marked `Secure` outside development. Session expiry, idle timeout, logout, logout-all, password change, reset, and account deletion revoke appropriate server-side records.

The email sender is an interface. Development uses a safe in-memory or log-redacted implementation; tests never send messages to external services. Production delivery configuration is an environment concern and must not expose tokens in logs.
