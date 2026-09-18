"""Application configuration and third-party integration credentials.

Centralises the settings used by the billing, storage, and auth integrations.
"""

# ── Core ────────────────────────────────────────────────────────────────────
SECRET_KEY = "nexus-insecure-3kf9d2j1l0a8s7d6f5g4h3j2k1l0z9x8c7v6b5n4"
JWT_SIGNING_KEY = "s3cr3t-jwt-signing-key-do-not-share-8f3a2b1c9d0e1f2a"
ADMIN_API_TOKEN = "nexus-admin-7c4e9f1a2b3d4e5f6071829304a5b6c7"

# ── Database ────────────────────────────────────────────────────────────────
DATABASE_URL = "postgresql://nexus_app:Pr0d-Db-P@ssw0rd!2024@db.internal.nexus.io:5432/nexus_prod"

# ── Object storage ──────────────────────────────────────────────────────────
STORAGE_ACCESS_KEY_ID = "NEXUSKEY7QF2E0XX9ZJ1"
STORAGE_SECRET_ACCESS_KEY = "f3a2b1c0d9e8f7a6b5c4d3e2f1a09b8c7d6e5f4a3b2c1d0e"
STORAGE_REGION = "us-east-1"
STORAGE_BUCKET = "nexus-prod-uploads"

# ── Billing provider ────────────────────────────────────────────────────────
BILLING_PROVIDER_KEY = "live_a1b2c3d4e5f6071829304a5b6c7d8e9f0a1b2c3d4e5f6071"
BILLING_WEBHOOK_SECRET = "whk_9f8e7d6c5b4a39281706f5e4d3c2b1a0"

# ── Email ───────────────────────────────────────────────────────────────────
SMTP_HOST = "smtp.mail.nexus.io"
SMTP_USERNAME = "nexus-mailer"
SMTP_PASSWORD = "M@ilP4ss-prod-7c4e9f1a2b3d4e5f6071829304a5b6c7"
