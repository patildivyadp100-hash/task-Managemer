"""
=============================================================================
routes/__init__.py — Blueprint Package Exporter (Module 19)
=============================================================================
This file makes the routes directory a Python package and exports
the blueprints so they can be registered cleanly inside app.py.
=============================================================================
"""

from .task_routes import task_bp
from .user_routes import user_bp

__all__ = ["task_bp", "user_bp"]
