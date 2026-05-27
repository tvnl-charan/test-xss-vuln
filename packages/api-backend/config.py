"""
Application configuration — loaded from environment variables.

Security-sensitive defaults are intentionally weak for local development.
Production deployments MUST override via env vars.
"""

import os

# ── Database ──────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nexus.db")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))

# ── Auth ──────────────────────────────────────────────────────────────────────

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = int(os.getenv("JWT_EXPIRY_MINUTES", "60"))
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "nexus-admin-dev-key-2024")

# ── File uploads ──────────────────────────────────────────────────────────────

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/nexus-uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".csv"}

# ── External services ────────────────────────────────────────────────────────

WEBHOOK_TIMEOUT_SECONDS = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ── Rate limiting ─────────────────────────────────────────────────────────────

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT", "60"))

# ── Feature flags ─────────────────────────────────────────────────────────────

ENABLE_ADMIN_PANEL = os.getenv("ENABLE_ADMIN_PANEL", "true").lower() == "true"
ENABLE_WEBHOOKS = os.getenv("ENABLE_WEBHOOKS", "true").lower() == "true"
ENABLE_FILE_UPLOADS = os.getenv("ENABLE_FILE_UPLOADS", "true").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
