"""
WSGI config for the FleetCare AI backend.

Exposes the WSGI callable as a module-level variable named ``application``.
gunicorn start command: gunicorn backend.wsgi:application
"""

import os

# Load .env if present (local dev or docker).
# On Render, env vars are injected by the platform — this is a safe no-op.
try:
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()  # fallback to current working directory
except ImportError:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()