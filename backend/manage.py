#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

    # Load .env file for local development (python-dotenv).
    # In production (Render), env vars are injected by the platform — dotenv is a no-op.
    try:
        from dotenv import load_dotenv
        from pathlib import Path
        env_path = Path(__file__).resolve().parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()  # fallback to current working directory
    except ImportError:
        pass  # dotenv not installed in this environment — that's fine

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()