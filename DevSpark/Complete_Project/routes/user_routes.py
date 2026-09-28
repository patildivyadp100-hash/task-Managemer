"""
=============================================================================
routes/user_routes.py — User Route Blueprint (Module 19, 20, 21, 22)
=============================================================================
Handles all User REST API endpoints.

Endpoints implemented:
  - POST /api/users               -> Create a new user (201 Created / 400 Bad Request)
  - GET  /api/users               -> List all users (200 OK)
  - GET  /api/users/<int:user_id> -> Get user details by ID (200 OK / 404 Not Found)
  - GET  /api/users/<int:user_id>/tasks -> Get all tasks assigned to user (User-Task rel)

Modules Covered:
  - Module 19: Blueprint Modularization
  - Module 20: REST API Endpoint Design
  - Module 21: Validation & Error Handling (Missing name/email, duplicates)
  - Module 22: Complete User CRUD
=============================================================================
"""

import sqlite3
from flask import Blueprint, request, jsonify

from database import (
    create_user,
    get_user_by_id,
    get_all_users,
    get_tasks_by_user
)
from models import user_to_dict, task_to_dict

# Initialize user blueprint
user_bp = Blueprint("users", __name__)


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@user_bp.route("/api/users", methods=["POST"])
@user_bp.route("/users", methods=["POST"])
def api_create_user():
    """
    POST /api/users
    Create a new user with name and unique email.

    Request Body (JSON):
      {
        "name": "Jane Doe",
        "email": "jane@example.com"
      }

    Validation rules:
      - Request body must be valid JSON
      - Name is required and cannot be empty string
      - Email is required and cannot be empty string
      - Email must not already exist in database (UNIQUE constraint)
    """
    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "error": "Invalid request body. Expected JSON object."
        }), 400

    name = data.get("name", "").strip() if isinstance(data.get("name"), str) else ""
    email = data.get("email", "").strip() if isinstance(data.get("email"), str) else ""

    # Validation: Name required
    if not name:
        return jsonify({
            "status": "error",
            "error": "User name is required."
        }), 400

    # Validation: Email required
    if not email:
        return jsonify({
            "status": "error",
            "error": "User email is required."
        }), 400

    # Simple email format sanity check
    if "@" not in email or "." not in email:
        return jsonify({
            "status": "error",
            "error": "A valid email address is required."
        }), 400

    try:
        new_id = create_user(name, email)
        user_row = get_user_by_id(new_id)

        return jsonify({
            "status": "success",
            "message": "User created successfully.",
            "user": user_to_dict(user_row)
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "status": "error",
            "error": f"Email '{email}' is already registered."
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"An error occurred while creating user: {str(e)}"
        }), 500


@user_bp.route("/api/users", methods=["GET"])
@user_bp.route("/users", methods=["GET"])
def api_list_users():
    """
    GET /api/users
    Retrieve all registered users.
    """
    users = get_all_users()
    return jsonify({
        "status": "success",
        "count": len(users),
        "users": [user_to_dict(u) for u in users]
    }), 200


@user_bp.route("/api/users/<int:user_id>", methods=["GET"])
@user_bp.route("/users/<int:user_id>", methods=["GET"])
def api_get_user(user_id):
    """
    GET /api/users/<id>
    Retrieve single user by ID. Returns 404 if not found.
    """
    user_row = get_user_by_id(user_id)

    if not user_row:
        return jsonify({
            "status": "error",
            "error": f"User with ID {user_id} was not found."
        }), 404

    return jsonify({
        "status": "success",
        "user": user_to_dict(user_row)
    }), 200


@user_bp.route("/api/users/<int:user_id>/tasks", methods=["GET"])
@user_bp.route("/users/<int:user_id>/tasks", methods=["GET"])
def api_get_user_tasks(user_id):
    """
    GET /api/users/<id>/tasks
    Demonstrates the User–Task relationship (Module 18 & 20):
    Fetches all tasks assigned to a specific user.
    """
    user_row = get_user_by_id(user_id)
    if not user_row:
        return jsonify({
            "status": "error",
            "error": f"User with ID {user_id} does not exist."
        }), 404

    tasks = get_tasks_by_user(user_id)
    return jsonify({
        "status": "success",
        "user": user_to_dict(user_row),
        "count": len(tasks),
        "tasks": [task_to_dict(t) for t in tasks]
    }), 200
