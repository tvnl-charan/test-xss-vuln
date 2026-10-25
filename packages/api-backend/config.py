"""Application configuration and third-party integration credentials.

Centralises the settings used by the billing, storage, and auth integrations.

Secrets are read from environment variables at runtime — never hardcode them
here. See ``.env.production.example`` for the full list of expected variables.
"""

import os

# ── Core ────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "")
JWT_SIGNING_KEY = os.environ.get("JWT_SIGNING_KEY", "")
ADMIN_API_TOKEN = os.environ.get("ADMIN_API_TOKEN", "")

# ── Database ────────────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")

# ── Object storage ──────────────────────────────────────────────────────────
STORAGE_ACCESS_KEY_ID = os.environ.get("STORAGE_ACCESS_KEY_ID", "")
STORAGE_SECRET_ACCESS_KEY = os.environ.get("STORAGE_SECRET_ACCESS_KEY", "")
STORAGE_REGION = os.environ.get("STORAGE_REGION", "us-east-1")
STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET", "nexus-prod-uploads")

# ── Billing provider ────────────────────────────────────────────────────────
BILLING_PROVIDER_KEY = os.environ.get("BILLING_PROVIDER_KEY", "")
BILLING_WEBHOOK_SECRET = os.environ.get("BILLING_WEBHOOK_SECRET", "")

# ── Email ───────────────────────────────────────────────────────────────────
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.mail.nexus.io")
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "nexus-mailer")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
