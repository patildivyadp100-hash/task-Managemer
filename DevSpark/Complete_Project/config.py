"""
=============================================================================
config.py — Application Configuration (Module 23: Production Readiness)
=============================================================================
This file centralizes all application configuration settings.

Why a separate config file?
  1. Separation of concerns: Keep configuration decoupled from application logic.
  2. Security: Never hardcode passwords, secret keys, or database credentials.
  3. Environment-based config: Easily switch between Local Development and Production
     using environment variables.

Modules Covered:
  - Module 03: Object-Oriented Programming (Class-based configuration)
  - Module 23: Production Readiness (Environment variables, Secret keys, Debug mode)
=============================================================================
"""

import os
import tempfile


class Config:
    """
    Base configuration class with defaults suitable for local development,
    overridable via system environment variables in production (e.g. on Render).
    """

    # Secret Key: used by Flask for session signing and Flask-WTF CSRF protection.
    # In production, set this in your host dashboard (Render/Vercel) to a random hex key:
    # python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-taskflow-2026")

    # SQLite Database filename / path:
    # On Vercel (serverless AWS Lambda environment), the root filesystem is read-only.
    # Writable files must be stored in /tmp. On Render or local development, use tasks.db.
    if os.environ.get("VERCEL"):
        DATABASE = os.environ.get("DATABASE", os.path.join(tempfile.gettempdir(), "tasks.db"))
    else:
        DATABASE = os.environ.get("DATABASE", "tasks.db")

    # Debug mode flag:
    # Defaults to True locally for hot-reload and informative traceback pages.
    # IN PRODUCTION, MUST BE SET TO False to prevent security vulnerabilities.
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
