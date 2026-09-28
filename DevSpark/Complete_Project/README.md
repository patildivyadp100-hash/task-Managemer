# ⚡ TaskFlow — Full-Stack Flask & SQLite Task Manager Backend

TaskFlow is a production-ready, modular Flask web application and REST API backend with SQLite database persistence, WTForms server-side validation, clean Blueprint architecture, and complete cloud deployment configurations.

---

## 🚀 Features

- **Database Persistence (Module 18)**: Native SQLite integration (`tasks.db`), relational tables (`users` and `tasks`) linked via Foreign Key constraints (`tasks.user_id -> users.id`).
- **Clean Architecture (Module 19)**: Distinct separation of responsibilities (`app.py`, `database.py`, `models.py`, `forms.py`, `config.py`, and `routes/`).
- **RESTful API (Module 20 & 22)**: Complete CRUD endpoints (`GET`, `POST`, `PUT`, `DELETE`) with JSON responses and standard HTTP status codes (`200`, `201`, `400`, `404`, `500`).
- **Validation & Error Handling (Module 21)**: Validates missing task titles, non-existent users, invalid statuses, and centralizes global error handlers for both API and browser clients.
- **Modern Responsive Web UI (Modules 13 & 14)**: Jinja2 template inheritance, interactive status filtering, search bar, and CSRF-protected forms.
- **Production Readiness (Module 23)**: Environment variable configuration for `SECRET_KEY`, `FLASK_DEBUG`, and production WSGI server via Gunicorn.
- **Deployment Ready (Modules 24, 25, 26)**: Includes Git configuration, Render `Procfile`, and Vercel `vercel.json`.

---

## 📁 Project Structure

```
Complete_Project/
├── app.py                # Main application entry point & blueprint registration
├── config.py             # Class-based config reading from environment variables
├── database.py           # SQLite connection, table initialization & CRUD operations
├── models.py             # Row serializers (task_to_dict, user_to_dict) & constants
├── forms.py              # Flask-WTF form classes with validation rules
├── requirements.txt      # Python dependencies (Flask, Flask-WTF, WTForms, gunicorn)
├── Procfile              # Render deployment start command: web: gunicorn app:app
├── vercel.json           # Vercel serverless deployment routing config
├── .gitignore            # Excludes venv, __pycache__, *.db, and secrets
├── .env.example          # Environment variable template
├── README.md             # Project documentation
├── DEPLOYMENT_GUIDE.md   # Step-by-step deployment guide for Render & Vercel
├── routes/
│   ├── __init__.py       # Exports task_bp and user_bp
│   ├── task_routes.py    # HTML routes and Task REST API endpoints
│   └── user_routes.py    # User REST API endpoints and sub-resources
├── templates/
│   ├── base.html         # Base template with responsive navigation & flash alerts
│   ├── index.html        # Dashboard with live metric counters & recent tasks
│   ├── tasks.html        # Filterable & searchable tasks table
│   ├── task_detail.html  # Single task detail view
│   ├── add_task.html     # Task creation form with WTForms validation
│   ├── edit_task.html    # Task editing form
│   ├── about.html        # Interactive API reference and architecture docs
│   ├── 404.html          # Custom 404 error page
│   └── 500.html          # Custom 500 error page
└── static/
    └── style.css         # Modern dark-mode responsive stylesheet
```

---

## 🛠️ Local Development Setup

### 1. Create and Activate Virtual Environment
```bash
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux:
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/users` | Register a new user (`name`, `email`) | `201 Created` |
| `GET` | `/api/users` | Retrieve all registered users | `200 OK` |
| `GET` | `/api/users/<id>` | Retrieve a single user by ID | `200 OK` / `404` |
| `GET` | `/api/users/<id>/tasks` | Retrieve all tasks assigned to a user | `200 OK` / `404` |
| `POST` | `/api/tasks` | Create a new task (`title`, `description`, `status`, `user_id`) | `201 Created` |
| `GET` | `/api/tasks` | List all tasks (supports `?status=pending`) | `200 OK` |
| `GET` | `/api/tasks/<id>` | Retrieve a single task by ID | `200 OK` / `404` |
| `PUT` | `/api/tasks/<id>` | Update an existing task | `200 OK` / `404` |
| `DELETE` | `/api/tasks/<id>` | Delete a task by ID | `200 OK` / `404` |

---

## 🚀 Cloud Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full walkthroughs:
- **Render (Mandatory/Production)**: Deploy as a 24/7 web service with persistent backend.
- **Vercel (Serverless Demo)**: Deploy as an on-demand serverless function.
