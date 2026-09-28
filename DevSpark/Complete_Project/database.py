"""
=============================================================================
database.py — Database Initialization & CRUD Layer
=============================================================================
This file handles all direct interactions with the SQLite database.

Why a dedicated database file?
  - Separation of Concerns (Module 19): Route functions don't write raw SQL.
  - Reusability: Database queries can be invoked from Web views, REST APIs,
    or CLI scripts without duplicating SQL code.
  - Security: All queries use parameterized queries (? placeholders) to prevent
    SQL injection attacks.

Modules Covered:
  - Module 17: SQL Basics (CREATE, INSERT, SELECT, UPDATE, DELETE)
  - Module 18: SQLite + Flask Integration (Connection, Row factory, Foreign Keys)
  - Module 22: Complete CRUD Operations
=============================================================================
"""
import os
import sqlite3
import tempfile
from flask import current_app

DATABASE_NAME = os.path.join(tempfile.gettempdir(), "tasks.db") if os.environ.get("VERCEL") else "tasks.db"


def _init_schema(conn):
    """Internal helper to initialize tables and initial seed data."""
    cursor = conn.cursor()

    # Table 1: users (Module 18)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Table 2: tasks (Module 18 — User-Task relationship via FOREIGN KEY)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        );
    """)

    # Seed initial demo user and task if empty so serverless instances aren't blank
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, name, email)
        VALUES (1, 'Alice Smith', 'alice@example.com');
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO tasks (id, user_id, title, description, status)
        VALUES (1, 1, 'Welcome to TaskFlow!', 'Explore the dashboard, create tasks, and test the REST API endpoints.', 'pending');
    """)
    conn.commit()


def get_db():
    """
    Establish and return a connection to the SQLite database.

    sqlite3.Row allows column access by name (e.g. row['title'])
    rather than numeric tuple index (e.g. row[2]).
    """
    # Use database path configured in Flask config, or fall back to default
    try:
        db_path = current_app.config.get("DATABASE", DATABASE_NAME)
    except RuntimeError:
        db_path = DATABASE_NAME

    # Ensure parent directory exists (especially for /tmp paths in serverless)
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # Check if database needs initialization (crucial for ephemeral serverless environments)
    need_init = not os.path.exists(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable SQLite Foreign Key constraint enforcement
    conn.execute("PRAGMA foreign_keys = ON;")

    if need_init:
        _init_schema(conn)

    return conn


def init_db():
    """
    Initialize tables in tasks.db if they do not already exist.

    Schema:
      1. users: id, name, email (UNIQUE), created_at
      2. tasks: id, user_id (FK to users.id), title, description, status, created_at
    """
    conn = get_db()
    _init_schema(conn)
    conn.close()


# =============================================================================
# USER CRUD OPERATIONS (Module 18, 20, 22)
# =============================================================================

def create_user(name, email):
    """
    Insert a new user.
    Returns: The newly created user's integer ID.
    Raises: sqlite3.IntegrityError if email is duplicated.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email) VALUES (?, ?);",
        (name, email)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_user_by_id(user_id):
    """
    Retrieve a single user row by their primary key ID.
    Returns: sqlite3.Row or None
    """
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?;",
        (user_id,)
    ).fetchone()
    conn.close()
    return user


def get_all_users():
    """
    Retrieve all users registered in the database, ordered by ID ascending.
    Returns: List of sqlite3.Row objects
    """
    conn = get_db()
    users = conn.execute(
        "SELECT * FROM users ORDER BY id ASC;"
    ).fetchall()
    conn.close()
    return users


# =============================================================================
# TASK CRUD OPERATIONS (Module 18, 20, 21, 22)
# =============================================================================

def create_task(title, description="", status="pending", user_id=None):
    """
    Insert a new task into tasks.db.
    Returns: The new task's primary key ID.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (title, description, status, user_id)
        VALUES (?, ?, ?, ?);
        """,
        (title, description, status, user_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_tasks():
    """
    Retrieve all tasks joined with assigned user name, ordered newest first.
    Returns: List of sqlite3.Row objects
    """
    conn = get_db()
    tasks = conn.execute("""
        SELECT tasks.*, users.name AS user_name, users.email AS user_email
        FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
        ORDER BY tasks.id DESC;
    """).fetchall()
    conn.close()
    return tasks


def get_task_by_id(task_id):
    """
    Retrieve a single task by ID joined with assigned user info.
    Returns: sqlite3.Row or None
    """
    conn = get_db()
    task = conn.execute("""
        SELECT tasks.*, users.name AS user_name, users.email AS user_email
        FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
        WHERE tasks.id = ?;
    """, (task_id,)).fetchone()
    conn.close()
    return task


def get_tasks_by_status(status):
    """
    Retrieve tasks filtered by status ('pending', 'in_progress', 'completed').
    Returns: List of sqlite3.Row objects
    """
    conn = get_db()
    tasks = conn.execute("""
        SELECT tasks.*, users.name AS user_name, users.email AS user_email
        FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
        WHERE tasks.status = ?
        ORDER BY tasks.id DESC;
    """, (status,)).fetchall()
    conn.close()
    return tasks


def get_tasks_by_user(user_id):
    """
    Retrieve all tasks assigned to a specific user (User–Task relationship).
    Returns: List of sqlite3.Row objects
    """
    conn = get_db()
    tasks = conn.execute("""
        SELECT tasks.*, users.name AS user_name, users.email AS user_email
        FROM tasks
        LEFT JOIN users ON tasks.user_id = users.id
        WHERE tasks.user_id = ?
        ORDER BY tasks.id DESC;
    """, (user_id,)).fetchall()
    conn.close()
    return tasks


def search_tasks(query, status=None):
    """
    Search tasks matching query text in title or description.
    Optionally filters by status.
    Returns: List of sqlite3.Row objects
    """
    conn = get_db()
    pattern = f"%{query}%"

    if status and status in ("pending", "in_progress", "completed"):
        tasks = conn.execute("""
            SELECT tasks.*, users.name AS user_name, users.email AS user_email
            FROM tasks
            LEFT JOIN users ON tasks.user_id = users.id
            WHERE (tasks.title LIKE ? OR tasks.description LIKE ?)
              AND tasks.status = ?
            ORDER BY tasks.id DESC;
        """, (pattern, pattern, status)).fetchall()
    else:
        tasks = conn.execute("""
            SELECT tasks.*, users.name AS user_name, users.email AS user_email
            FROM tasks
            LEFT JOIN users ON tasks.user_id = users.id
            WHERE tasks.title LIKE ? OR tasks.description LIKE ?
            ORDER BY tasks.id DESC;
        """, (pattern, pattern)).fetchall()

    conn.close()
    return tasks


def get_task_counts():
    """
    Return statistics of task counts (total, pending, in_progress, completed).
    Useful for dashboard display.
    """
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM tasks;").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending';").fetchone()[0]
    in_progress = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress';").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed';").fetchone()[0]
    conn.close()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed
    }


def update_task(task_id, title, description, status, user_id=None):
    """
    Update title, description, status, and assigned user for an existing task.
    """
    conn = get_db()
    conn.execute("""
        UPDATE tasks
        SET title = ?, description = ?, status = ?, user_id = ?
        WHERE id = ?;
    """, (title, description, status, user_id, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id):
    """
    Delete a task by primary key ID.
    """
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
    conn.commit()
    conn.close()
