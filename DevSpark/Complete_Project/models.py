"""
=============================================================================
models.py — Data Serializers & Business Constants
=============================================================================
This file defines serialization helpers that transform SQLite row objects
into standard Python dictionaries suitable for JSON APIs, as well as domain
constants.

Why is this needed?
  - sqlite3.Row objects cannot be serialized directly by flask.jsonify().
  - Serializing via explicit functions gives us control over which fields are
    exposed, formatted, or omitted in our REST APIs (Module 20).

Modules Covered:
  - Module 04: Python Dictionaries and JSON Serialization
  - Module 18: SQLite Data Conversion for Flask
  - Module 20: REST API Data Modeling
=============================================================================
"""

# Valid task lifecycle statuses across the application
VALID_STATUSES = ["pending", "in_progress", "completed"]


def task_to_dict(task):
    """
    Convert a sqlite3.Row task object into a JSON-serializable dictionary.
    Includes user information if joined.
    """
    if task is None:
        return None

    data = {
        "id": task["id"],
        "user_id": task["user_id"],
        "title": task["title"],
        "description": task["description"] or "",
        "status": task["status"],
        "created_at": task["created_at"]
    }

    # Add optional joined user information if available
    try:
        if "user_name" in task.keys() and task["user_name"]:
            data["user_name"] = task["user_name"]
            data["user_email"] = task["user_email"]
    except (IndexError, KeyError):
        pass

    return data


def user_to_dict(user):
    """
    Convert a sqlite3.Row user object into a JSON-serializable dictionary.
    """
    if user is None:
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"]
    }
