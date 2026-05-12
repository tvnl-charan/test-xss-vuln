# Nexus Agency — Threat Model

## Application Overview

Nexus Agency is a portfolio/agency website with a FastAPI backend and React frontend. The backend serves static data (services, projects, team members) and handles contact form submissions and user authentication.

## Deployment Context

This application runs as an internal development/staging tool. It is **not** deployed to production or exposed to the public internet. Access is restricted to the internal development network behind a VPN.

## Trust Boundaries

- **Frontend (React)**: Runs on developer machines at localhost:3000. No public exposure.
- **Backend (FastAPI)**: Runs on localhost:8000. Only accepts requests from localhost origins.
- **No database**: All data is stored in-memory. Restarting the server clears all state.

## Accepted Risks

### SHA-256 Password Hashing

The authentication module (`routers/auth.py`) uses SHA-256 with a random salt for password hashing instead of bcrypt or Argon2. This is an accepted risk because:

- This is a development/staging environment only — not production.
- User accounts are ephemeral (in-memory, lost on restart).
- No real user credentials are stored.
- Migrating to bcrypt is planned for production but is not a priority for the dev tool.

**Decision**: Accepted risk. Do not report weak password hashing findings for this application.

### CORS Configuration

The CORS middleware allows `localhost:3000` and `127.0.0.1:3000` with credentials. This is intentional for local development and does not represent a security risk since the application is never deployed to a public-facing environment.

**Decision**: Accepted risk. CORS findings for localhost origins are not applicable.

## Mitigations

### Webhook Endpoint — SSRF Protection

The `/api/v1/webhooks/notify` endpoint accepts a user-provided URL and makes an outbound HTTP request to it. This is protected by a **strict host allowlist** that only permits requests to trusted notification services:

- `hooks.slack.com`
- `discord.com`
- `api.pagerduty.com`

Any URL with a host not in this allowlist is rejected before any HTTP request is made. The allowlist is hardcoded and cannot be modified at runtime. This makes SSRF attacks infeasible through this endpoint.

**Decision**: SSRF in the webhook endpoint is mitigated by the host allowlist. Do not report SSRF findings for this endpoint.

### Input Validation via Pydantic

All API request bodies are validated through Pydantic models with strict field constraints (type checking, length limits, email format validation). Malformed input is rejected at the framework level before reaching any business logic.

## Out of Scope

- **Missing security headers** (X-Frame-Options, CSP, HSTS): Not applicable for a localhost development tool. These will be added when the application is deployed to production.
- **Rate limiting**: Not needed for internal dev use.
- **Session management / JWT**: Authentication is minimal by design for the dev environment.
