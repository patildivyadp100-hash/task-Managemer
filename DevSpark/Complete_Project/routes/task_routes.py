"""
=============================================================================
routes/task_routes.py — Task Route Blueprint (Modules 11, 12, 13, 14, 15, 20, 21, 22)
=============================================================================
This file houses both the HTML views (Web App) and JSON endpoints (REST API)
for task management.

Modules Covered:
  - Module 11: Flask Routing (Static and Dynamic with <int:task_id>)
  - Module 12: Query Parameters (request.args for filtering & searching)
  - Module 13: Jinja2 Templates (render_template, flash messages, redirects)
  - Module 14: Flask-WTF Form Handling & Validation
  - Module 15: APIs & JSON (jsonify, request.get_json)
  - Module 20: REST API Design (POST, GET, PUT, DELETE)
  - Module 21: Validation & Error Handling (Missing title, invalid status, invalid user ID)
  - Module 22: Complete CRUD Backend Integration
=============================================================================
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from database import (
    get_all_tasks,
    get_task_by_id,
    get_tasks_by_status,
    get_task_counts,
    search_tasks,
    create_task,
    update_task,
    delete_task,
    get_all_users,
    get_user_by_id
)
from models import task_to_dict, VALID_STATUSES
from forms import AddTaskForm, EditTaskForm

# Initialize task blueprint
task_bp = Blueprint("tasks", __name__)


# =============================================================================
# HELPER: Check if client expects JSON
# =============================================================================

def is_json_request():
    """Detect if the current request is seeking a JSON payload."""
    return (
        request.is_json
        or request.headers.get("Accept") == "application/json"
        or request.path.startswith("/api/")
    )


# =============================================================================
# HTML WEB INTERFACE ROUTES (Modules 10, 11, 12, 13, 14, 22)
# =============================================================================

@task_bp.route("/")
def home():
    """
    Dashboard view displaying real-time task statistics and quick links.
    """
    counts = get_task_counts()
    recent_tasks = get_all_tasks()[:5]  # Show the 5 latest tasks
    return render_template("index.html", counts=counts, recent_tasks=recent_tasks)


@task_bp.route("/about")
def about():
    """
    About page detailing the tech stack and interactive API reference.
    """
    return render_template("about.html")


@task_bp.route("/tasks")
def list_tasks():
    """
    HTML view of tasks table with status tabs filter (?status=pending).
    """
    # If a REST API client requests /tasks with Accept: application/json, return JSON
    if is_json_request() and not request.accept_mimetypes.accept_html:
        return api_get_tasks()

    status_filter = request.args.get("status")

    if status_filter and status_filter in VALID_STATUSES:
        tasks = get_tasks_by_status(status_filter)
    else:
        status_filter = None
        tasks = get_all_tasks()

    counts = get_task_counts()
    return render_template(
        "tasks.html",
        tasks=tasks,
        current_status=status_filter,
        counts=counts,
        search_query=""
    )


@task_bp.route("/tasks/search")
def search():
    """
    HTML view searching tasks by title or description (?q=keyword).
    """
    query = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip() or None

    tasks = search_tasks(query, status) if query else get_all_tasks()
    counts = get_task_counts()

    return render_template(
        "tasks.html",
        tasks=tasks,
        current_status=status,
        counts=counts,
        search_query=query
    )


@task_bp.route("/tasks/<int:task_id>")
def task_detail(task_id):
    """
    HTML view for a single task detail page.
    """
    task = get_task_by_id(task_id)
    if not task:
        flash(f"Task #{task_id} not found.", "error")
        return redirect(url_for("tasks.list_tasks"))

    return render_template("task_detail.html", task=task)


@task_bp.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    """
    HTML view with WTForms validation to create a new task.
    """
    form = AddTaskForm()

    # Populate assigned user choices dynamically from SQLite
    users = get_all_users()
    form.user_id.choices = [(0, "-- Unassigned --")] + [(u["id"], u["name"]) for u in users]

    if form.validate_on_submit():
        user_id = form.user_id.data if form.user_id.data > 0 else None
        new_id = create_task(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
            status="pending",
            user_id=user_id
        )
        flash(f"Task '{form.title.data}' created successfully!", "success")
        return redirect(url_for("tasks.task_detail", task_id=new_id))

    return render_template("add_task.html", form=form)


@task_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    """
    HTML view with WTForms validation to update an existing task.
    """
    task = get_task_by_id(task_id)
    if not task:
        flash("Task not found.", "error")
        return redirect(url_for("tasks.list_tasks"))

    form = EditTaskForm()
    users = get_all_users()
    form.user_id.choices = [(0, "-- Unassigned --")] + [(u["id"], u["name"]) for u in users]

    if form.validate_on_submit():
        user_id = form.user_id.data if form.user_id.data > 0 else None
        update_task(
            task_id=task_id,
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else "",
            status=form.status.data,
            user_id=user_id
        )
        flash("Task updated successfully!", "success")
        return redirect(url_for("tasks.task_detail", task_id=task_id))

    # Pre-populate form fields on GET
    if request.method == "GET":
        form.title.data = task["title"]
        form.description.data = task["description"]
        form.status.data = task["status"]
        form.user_id.data = task["user_id"] or 0

    return render_template("edit_task.html", form=form, task=task)


@task_bp.route("/tasks/<int:task_id>/delete", methods=["GET", "POST"])
def delete_task_route(task_id):
    """
    HTML action to delete a task.
    """
    task = get_task_by_id(task_id)
    if not task:
        flash(f"Task #{task_id} not found.", "error")
    else:
        delete_task(task_id)
        flash(f"Task #{task_id} deleted successfully.", "success")

    return redirect(url_for("tasks.list_tasks"))


# =============================================================================
# REST API ENDPOINTS (Modules 15, 20, 21, 22)
# =============================================================================

@task_bp.route("/api/tasks", methods=["POST"])
def api_create_task():
    """
    POST /api/tasks
    Create a new task via JSON payload.

    Expected JSON body:
      {
        "title": "Build REST API",
        "description": "Optional notes",
        "status": "pending",
        "user_id": 1
      }

    Validation rules (Module 21):
      - Missing or invalid JSON body -> 400 Bad Request
      - Missing task title -> 400 Bad Request
      - Invalid status value -> 400 Bad Request
      - Invalid user_id (user does not exist) -> 400 Bad Request
    """
    data = request.get_json(silent=True)

    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "error": "Invalid request body. Expected JSON object."
        }), 400

    title = data.get("title", "").strip() if isinstance(data.get("title"), str) else ""

    # Validation: Missing task title
    if not title:
        return jsonify({
            "status": "error",
            "error": "Task title is required."
        }), 400

    # Validation: Invalid task status
    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        return jsonify({
            "status": "error",
            "error": f"Invalid task status '{status}'. Allowed statuses: {VALID_STATUSES}"
        }), 400

    # Validation: Invalid user ID
    user_id = data.get("user_id")
    if user_id is not None:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "error": "user_id must be a valid integer."
            }), 400

        user_exists = get_user_by_id(user_id)
        if not user_exists:
            return jsonify({
                "status": "error",
                "error": f"Invalid user_id: User with ID {user_id} does not exist."
            }), 400

    description = data.get("description", "")
    if description is None:
        description = ""

    task_id = create_task(title, str(description), status, user_id)
    new_task = get_task_by_id(task_id)

    return jsonify({
        "status": "success",
        "message": "Task created successfully.",
        "task": task_to_dict(new_task)
    }), 201


@task_bp.route("/api/tasks", methods=["GET"])
def api_get_tasks():
    """
    GET /api/tasks
    Retrieve all tasks, optionally filtered by ?status=pending
    """
    status = request.args.get("status")

    if status:
        if status not in VALID_STATUSES:
            return jsonify({
                "status": "error",
                "error": f"Invalid status filter '{status}'. Allowed statuses: {VALID_STATUSES}"
            }), 400
        tasks = get_tasks_by_status(status)
    else:
        tasks = get_all_tasks()

    return jsonify({
        "status": "success",
        "count": len(tasks),
        "tasks": [task_to_dict(t) for t in tasks]
    }), 200


@task_bp.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):
    """
    GET /api/tasks/<id>
    Retrieve a single task by primary key ID.
    Returns 404 if the task does not exist.
    """
    task = get_task_by_id(task_id)

    if not task:
        return jsonify({
            "status": "error",
            "error": f"Task with ID {task_id} was not found."
        }), 404

    return jsonify({
        "status": "success",
        "task": task_to_dict(task)
    }), 200


@task_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):
    """
    PUT /api/tasks/<id>
    Update an existing task's title, description, status, or assigned user.

    Validation rules (Module 21):
      - Non-existent task -> 404 Not Found
      - Invalid JSON body -> 400 Bad Request
      - Invalid status (if supplied) -> 400 Bad Request
      - Invalid user_id (if supplied) -> 400 Bad Request
    """
    task = get_task_by_id(task_id)

    if not task:
        return jsonify({
            "status": "error",
            "error": f"Task with ID {task_id} was not found."
        }), 404

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "error": "Request body must be a valid JSON object."
        }), 400

    title = data.get("title", task["title"])
    if not str(title).strip():
        return jsonify({
            "status": "error",
            "error": "Task title cannot be empty."
        }), 400

    description = data.get("description", task["description"])
    status = data.get("status", task["status"])

    if status not in VALID_STATUSES:
        return jsonify({
            "status": "error",
            "error": f"Invalid status '{status}'. Allowed statuses: {VALID_STATUSES}"
        }), 400

    # User assignment validation
    user_id = data.get("user_id", task["user_id"])
    if user_id is not None:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "error": "user_id must be a valid integer."
            }), 400

        user_exists = get_user_by_id(user_id)
        if not user_exists:
            return jsonify({
                "status": "error",
                "error": f"Invalid user_id: User with ID {user_id} does not exist."
            }), 400

    update_task(task_id, str(title).strip(), str(description or ""), status, user_id)
    updated_task = get_task_by_id(task_id)

    return jsonify({
        "status": "success",
        "message": "Task updated successfully.",
        "task": task_to_dict(updated_task)
    }), 200


@task_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):
    """
    DELETE /api/tasks/<id>
    Delete an existing task by ID.
    Returns 404 if the task does not exist.
    """
    task = get_task_by_id(task_id)

    if not task:
        return jsonify({
            "status": "error",
            "error": f"Task with ID {task_id} was not found."
        }), 404

    delete_task(task_id)

    return jsonify({
        "status": "success",
        "message": f"Task with ID {task_id} was deleted successfully."
    }), 200
