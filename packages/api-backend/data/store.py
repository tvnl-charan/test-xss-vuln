"""
Static content data and in-memory stores.

In a production app, replace the static lists with database queries
and contact_submissions with a proper persistence layer.
"""

# ── Stats ─────────────────────────────────────────────────────────────────────

STATS: list[dict] = [
    {"value": "200+", "label": "Projects Delivered"},
    {"value": "98%",  "label": "Client Satisfaction"},
    {"value": "5+",   "label": "Years of Experience"},
    {"value": "40+",  "label": "Team Members"},
]

# ── Services ──────────────────────────────────────────────────────────────────

SERVICES: list[dict] = [
    {
        "id": "web-development",
        "icon": "⬡",
        "title": "Web Development",
        "description": (
            "High-performance web apps built with React, Next.js, and modern backend "
            "technologies. Optimised for speed, SEO, and scalability."
        ),
        "tags": ["React", "Node.js", "PostgreSQL"],
    },
    {
        "id": "mobile-development",
        "icon": "◎",
        "title": "Mobile Development",
        "description": (
            "Cross-platform mobile apps for iOS and Android using React Native. "
            "Native feel, single codebase, fast delivery."
        ),
        "tags": ["React Native", "iOS", "Android"],
    },
    {
        "id": "ui-ux-design",
        "icon": "◈",
        "title": "UI / UX Design",
        "description": (
            "Research-driven design that prioritises clarity, usability, and visual "
            "delight — from wireframes to polished design systems."
        ),
        "tags": ["Figma", "Design Systems", "Prototyping"],
    },
    {
        "id": "cloud-devops",
        "icon": "◐",
        "title": "Cloud & DevOps",
        "description": (
            "Scalable cloud infrastructure on AWS, GCP, or Azure. "
            "CI/CD pipelines, containerisation, and real-time monitoring."
        ),
        "tags": ["AWS", "Docker", "Kubernetes"],
    },
    {
        "id": "ai-integration",
        "icon": "◑",
        "title": "AI Integration",
        "description": (
            "Embed intelligent features into your product — NLP, recommendations, "
            "computer vision, and predictive analytics."
        ),
        "tags": ["OpenAI", "TensorFlow", "Python"],
    },
    {
        "id": "security-audits",
        "icon": "◇",
        "title": "Security Audits",
        "description": (
            "Comprehensive security reviews including penetration testing, "
            "code audits, and compliance assessments."
        ),
        "tags": ["OWASP", "Pen Testing", "Compliance"],
    },
]

# ── Projects ──────────────────────────────────────────────────────────────────

PROJECTS: list[dict] = [
    {
        "id": "fintrack",
        "title": "FinTrack",
        "category": "Web",
        "description": (
            "A real-time financial dashboard for tracking investments, expenses, "
            "and portfolio performance at a glance."
        ),
        "tags": ["React", "Node.js", "Charts"],
        "accent": "#7c6fff",
    },
    {
        "id": "healthpulse",
        "title": "HealthPulse",
        "category": "Mobile",
        "description": (
            "Patient management app for clinics with appointment scheduling, "
            "EMR integration, and telemedicine."
        ),
        "tags": ["React Native", "Firebase"],
        "accent": "#00e5ff",
    },
    {
        "id": "katalog",
        "title": "Katalog",
        "category": "Design",
        "description": (
            "Complete design system and brand identity for a European e-commerce "
            "startup expanding across 8 markets."
        ),
        "tags": ["Figma", "Design System", "Branding"],
        "accent": "#ff6eb4",
    },
    {
        "id": "lexai",
        "title": "LexAI",
        "category": "AI",
        "description": (
            "AI-powered legal document analysis that flags risks and extracts "
            "key clauses in seconds, not hours."
        ),
        "tags": ["Python", "OpenAI", "NLP"],
        "accent": "#ffb347",
    },
    {
        "id": "shipfast",
        "title": "ShipFast",
        "category": "Web",
        "description": (
            "Order management platform for logistics companies with live GPS tracking, "
            "analytics, and driver apps."
        ),
        "tags": ["Next.js", "PostgreSQL", "WebSockets"],
        "accent": "#7c6fff",
    },
    {
        "id": "eduflow",
        "title": "EduFlow",
        "category": "Mobile",
        "description": (
            "Adaptive learning platform with personalised quizzes, progress tracking, "
            "and full offline support."
        ),
        "tags": ["React Native", "Redux", "Offline"],
        "accent": "#00e5ff",
    },
]

# ── Team ──────────────────────────────────────────────────────────────────────

TEAM: list[dict] = [
    {"id": "alex-chen",  "name": "Alex Chen",  "role": "CEO & Founder",            "initials": "AC"},
    {"id": "sara-patel", "name": "Sara Patel", "role": "Chief Technology Officer", "initials": "SP"},
    {"id": "marcus-lee", "name": "Marcus Lee", "role": "Lead Designer",            "initials": "ML"},
    {"id": "priya-nair", "name": "Priya Nair", "role": "Head of Engineering",      "initials": "PN"},
    {"id": "james-wu",   "name": "James Wu",   "role": "Product Strategist",       "initials": "JW"},
    {"id": "lena-kovac", "name": "Lena Kovac", "role": "DevOps Lead",              "initials": "LK"},
]

# ── Plans & billing catalogue ────────────────────────────────────────────────

PLANS: list[dict] = [
    {"id": "starter",      "name": "Starter",      "monthly_usd": 0,    "seats": 1},
    {"id": "team",         "name": "Team",         "monthly_usd": 49,   "seats": 10},
    {"id": "business",     "name": "Business",     "monthly_usd": 199,  "seats": 50},
    {"id": "enterprise",   "name": "Enterprise",   "monthly_usd": 999,  "seats": 500},
]

COUPONS: list[dict] = [
    {"code": "LAUNCH20",  "percent_off": 20, "active": True},
    {"code": "PARTNER50", "percent_off": 50, "active": True},
    {"code": "EXPIRED10", "percent_off": 10, "active": False},
]

# ── In-memory stores (swap for a DB in production) ───────────────────────────

contact_submissions: list[dict] = []
users: list[dict] = []
testimonials: list[dict] = []

# Admin / RBAC
roles: list[dict] = [
    {"id": "role-admin",  "name": "admin",  "permissions": ["*"]},
    {"id": "role-editor", "name": "editor", "permissions": ["projects:write", "testimonials:write"]},
    {"id": "role-viewer", "name": "viewer", "permissions": ["projects:read"]},
]

# Auth hardening surface
api_tokens: list[dict] = []
password_reset_tokens: list[dict] = []
sessions: list[dict] = []

# Assets / uploads
assets: list[dict] = []

# Notifications
notification_log: list[dict] = []
webhook_endpoints: list[dict] = []
webhook_delivery_queue: list[dict] = []

# Billing runtime state
invoices: list[dict] = []
subscriptions: list[dict] = []

# Reporting
report_jobs: list[dict] = []

# Sync / integrations
sync_jobs: list[dict] = []
