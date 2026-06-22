"""
settings.py — Production-hardened configuration for FleetCare AI Platform.

Environment-aware: reads all secrets and runtime configuration from
environment variables so no secrets are ever committed to source control.

Local development: copy .env.example → .env and fill in values.
Production (Render): set env vars in the Render dashboard.
"""

import os
from datetime import timedelta
from pathlib import Path

# ── Core ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── Phase 1: DEBUG ────────────────────────────────────────────────────────────
# Never hard-code True in production. Set DJANGO_DEBUG=True only locally.
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# ── Phase 2: SECRET KEY ───────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    if DEBUG:
        # Convenience fallback for local development ONLY.
        # This path is NEVER reachable in production because DEBUG=False
        # raises ImproperlyConfigured below before this branch can run.
        SECRET_KEY = "dev-only-key-not-used-in-production-replace-via-env-var"
    else:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(
            "SECRET_KEY environment variable is not set. "
            "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
        )

# ── Phase 3: ALLOWED HOSTS ────────────────────────────────────────────────────
# Comma-separated list in env var, e.g.:
#   ALLOWED_HOSTS=localhost,127.0.0.1,myfleet-platform.onrender.com
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",")

# Strip accidental whitespace from each entry
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS if h.strip()]

# ── Applications ──────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "accounts",
    "fleet",
    "telemetry",
    "predictions",
    "reports",
    "api",
]

# ── Middleware ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",             # must be first
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",         # static files on Render
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# ── Phase 4: DATABASE ─────────────────────────────────────────────────────────
# If DATABASE_URL is set (Render PostgreSQL), use it.
# Otherwise fall back to SQLite for local development.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=not DEBUG,   # require SSL in production
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ── Password Validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── i18n / Timezone ───────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Phase 7: Static Files ─────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: serve compressed static files from Render without a CDN
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Phase 6: CORS ─────────────────────────────────────────────────────────────
# Development: CORS_ALLOW_ALL_ORIGINS is allowed only when DEBUG=True.
# Production: set CORS_ALLOWED_ORIGINS in the env, e.g.:
#   CORS_ALLOWED_ORIGINS=https://myfleet.vercel.app,http://localhost:3000

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    _cors_raw = os.getenv("CORS_ALLOWED_ORIGINS", "")
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]

CORS_ALLOW_CREDENTIALS = True

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
}

AUTH_USER_MODEL = "accounts.User"

# ── Phase 5: JWT Hardening ────────────────────────────────────────────────────
# Lifetimes are configurable via environment variables.
# Signing key defaults to SECRET_KEY; never hardcode a separate value.

_jwt_access_minutes = int(os.getenv("JWT_ACCESS_MINUTES", "1440"))   # default: 1 day
_jwt_refresh_days   = int(os.getenv("JWT_REFRESH_DAYS",   "7"))

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=_jwt_access_minutes),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=_jwt_refresh_days),
    "ROTATE_REFRESH_TOKENS":  False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM":    "HS256",
    "SIGNING_KEY":  SECRET_KEY,     # derived from env — never hardcoded
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ── Production Security Headers ───────────────────────────────────────────────
# Only activate in production to avoid breaking local dev with HTTPS-only cookies.
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER           = True
    SECURE_CONTENT_TYPE_NOSNIFF         = True
    X_FRAME_OPTIONS                     = "DENY"
    SECURE_HSTS_SECONDS                 = 31536000   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS      = True
    SECURE_HSTS_PRELOAD                 = True
    # Render terminates TLS at their load balancer — Django sees HTTP internally.
    # Setting SECURE_SSL_REDIRECT=True here would cause infinite redirect loops.
    # Instead, trust X-Forwarded-Proto from Render's load balancer.
    SECURE_SSL_REDIRECT                 = False      # LB handles this
    SECURE_PROXY_SSL_HEADER             = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE               = True
    CSRF_COOKIE_SECURE                  = True

    # Silence W008 — SECURE_SSL_REDIRECT intentionally False (Render LB handles HTTPS)
    SILENCED_SYSTEM_CHECKS = ["security.W008"]
