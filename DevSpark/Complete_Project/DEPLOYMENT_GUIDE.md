# 🚀 Complete Deployment Guide: Modules 24, 25 & 26

This guide provides end-to-end instructions for deploying your Flask & SQLite backend to production.

---

## 📋 Overview of Deployment Flow

```
[Local Code in Complete_Project]
            │
            ▼  (Module 24)
      [Git & GitHub]
            │
            ├───► [Render Web Service] (Module 25 - Mandatory / Recommended)
            │         ↳ Runs Gunicorn WSGI 24/7 with SQLite persistence
            │
            └───► [Vercel Serverless] (Module 26 - Optional Demo)
                      ↳ Runs as ephemeral serverless Python functions
```

---

## 📌 PART 1: Git & GitHub Setup (Module 24)

### Step 1: Initialize Git inside the project directory
Open your terminal inside the `Complete_Project` folder:
```bash
cd Task_App/Complete_Project
git init
```

### Step 2: Verify `.gitignore`
Make sure `.gitignore` excludes temporary files and local database files:
```bash
# Check status — venv, *.db, and __pycache__ must NOT be listed
git status
```

> **Why exclude `*.db`?**
> Local `.db` files contain testing/mock data and shouldn't be tracked in version control. In serverless deployments (like Vercel), our code automatically initializes an empty database with seed data inside the writable `/tmp` directory at runtime.

### Step 3: Stage and Commit All Files
```bash
git add .
git commit -m "feat: complete TaskFlow backend with SQLite, REST API, and deployment configs"
```

### Step 4: Create a New GitHub Repository
1. Go to [https://github.com](https://github.com) and log in.
2. Click the **+** icon in the top right &rarr; **New repository**.
3. Repository name: `taskflow-backend` (or your preferred name).
4. Set visibility to **Public** (or Private).
5. **Do NOT** check "Add a README file" (we already created one).
6. Click **Create repository**.

### Step 5: Link Local Repo to GitHub & Push
```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/taskflow-backend.git
git push -u origin main
```

---

## 🌐 PART 2: Deploying to Render (Module 25 — Mandatory)

Render is a modern cloud hosting platform ideal for Flask applications because it runs a persistent server process (Gunicorn) that keeps your SQLite database alive.

### How Render Works with TaskFlow
- **Build Command**: `pip install -r requirements.txt` (Installs Flask, Flask-WTF, WTForms, and Gunicorn).
- **Start Command**: `gunicorn app:app` (Defined in `Procfile` to run a multi-worker production server).

### Step-by-Step Render Deployment:
1. Go to [https://render.com](https://render.com) and create an account (you can sign in with GitHub).
2. On your Render Dashboard, click **New +** &rarr; select **Web Service**.
3. Select **Build and deploy from a Git repository** &rarr; click **Next**.
4. Connect your GitHub account and select your `taskflow-backend` repository.
5. Fill in the deployment details:
   - **Name**: `taskflow-live` (or your custom name)
   - **Region**: Choose the region closest to you (e.g., Singapore, Frankfurt, Oregon)
   - **Branch**: `main`
   - **Root Directory**: (Leave blank if repo root contains `app.py`, or enter `Task_App/Complete_Project` if you pushed the whole workspace)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
6. Configure Environment Variables (Module 23):
   - Scroll down to **Environment Variables** &rarr; click **Add Environment Variable**.
   - Key: `SECRET_KEY`
     - Value: Generate a random string:
       ```bash
       python -c "import secrets; print(secrets.token_hex(32))"
       ```
   - Key: `FLASK_DEBUG`
     - Value: `False`
7. Click **Create Web Service**.
8. Render will now clone your repository, install dependencies, initialize SQLite, and launch Gunicorn!
9. Once the build completes, Render will provide your public live URL:
   `https://taskflow-live.onrender.com`

---

## ⚡ PART 3: Deploying to Vercel (Module 26 — Optional / Demo)

Vercel is primarily a serverless platform designed for frontend frameworks, but supports Python WSGI applications via `@vercel/python`.

### Understanding Serverless with Flask & SQLite
- On Render, the server runs continuously 24/7 with a persistent disk.
- On Vercel, requests trigger an **ephemeral serverless container** that spins down after seconds of inactivity.
- **Read-Only Root Filesystem**: In Vercel's serverless runtime (`/var/task`), the code directory is strictly read-only. SQLite cannot create or write to a database file in the project root.
- **The `/tmp` Solution**: The `/tmp` scratch directory is the only writable directory on Vercel. Our `config.py` detects `VERCEL=1` and routes SQLite to `/tmp/tasks.db`, while `database.py` auto-initializes the schema on first connection.
- **Important Limitation (Module 26)**: Files in `/tmp` are **ephemeral** and reset on container cold restarts. For permanent production persistence on serverless platforms, connect to a cloud database (like PostgreSQL on Neon or Supabase). For SQLite persistence, use **Render** (Part 2).
- **Required deployment check**: If the app is deployed on Vercel, make sure the runtime is configured to use the Vercel environment (the app checks `os.environ.get("VERCEL")` before choosing the database path).

### Configuration in `vercel.json`
We have included `vercel.json`:
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### Steps to Deploy to Vercel:
1. Go to [https://vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New...** &rarr; **Project**.
3. Import your `taskflow-backend` repository.
4. Set **Environment Variables**:
   - `VERCEL`: `1` (this tells Flask to write SQLite to `/tmp` instead of the read-only repo root)
   - `SECRET_KEY`: your random production key
   - `FLASK_DEBUG`: `False`
   - `DATABASE`: optional override, usually left blank so the app defaults to `/tmp/tasks.db`
5. Click **Deploy**.
6. Vercel will build and provide a live URL: `https://your-project.vercel.app`.

---

## ⚖️ Render vs Vercel: Platform Comparison

| Feature | Render (Web Service) | Vercel (Serverless) |
| :--- | :--- | :--- |
| **Architecture** | Persistent container / VM | On-demand serverless functions |
| **WSGI Server** | Gunicorn (`Procfile`) | `@vercel/python` serverless wrapper |
| **SQLite Support** | ✅ Works with local file persistence | ⚠️ Ephemeral: file resets on cold start |
| **Cold Starts** | Free tier sleeps after 15 min inactivity | Fast cold start (< 1 second) |
| **Best Used For** | Full-stack Flask apps, REST APIs, SQLite | Static sites, Next.js, APIs with cloud DB |
| **Role in Course** | **Mandatory & Recommended** | **Optional / Conceptual Demo** |

---

## 🧪 PART 4: Testing Your Live Backend

Once your app is deployed to Render, test both the Web UI and the REST API endpoints:

### 1. Test the Web Interface
Open your live URL in your browser:
```
https://YOUR-APP.onrender.com
```
- Verify the Dashboard loads with task metric cards.
- Click **+ New Task** and submit a task to confirm WTForms & SQLite write operations.
- Edit and delete a task to confirm full CRUD.

### 2. Test the Live REST APIs with cURL or Postman

#### A. Create a User (POST /api/users)
```bash
curl -X POST https://YOUR-APP.onrender.com/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Sarah Connor", "email": "sarah@skynet.com"}'
```
Expected response:
```json
{
  "status": "success",
  "message": "User created successfully.",
  "user": {
    "id": 1,
    "name": "Sarah Connor",
    "email": "sarah@skynet.com",
    "created_at": "..."
  }
}
```

#### B. Create a Task Linked to User (POST /api/tasks)
```bash
curl -X POST https://YOUR-APP.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Setup CI/CD pipeline", "description": "Automate tests on commit", "status": "pending", "user_id": 1}'
```
Expected response:
```json
{
  "status": "success",
  "message": "Task created successfully.",
  "task": {
    "id": 1,
    "user_id": 1,
    "title": "Setup CI/CD pipeline",
    "description": "Automate tests on commit",
    "status": "pending",
    "user_name": "Sarah Connor",
    "created_at": "..."
  }
}
```

#### C. List All Tasks (GET /api/tasks)
```bash
curl -X GET https://YOUR-APP.onrender.com/api/tasks
```

#### D. Filter Tasks by Status (GET /api/tasks?status=pending)
```bash
curl -X GET "https://YOUR-APP.onrender.com/api/tasks?status=pending"
```

#### E. Test Error Validation (POST /api/tasks with missing title)
```bash
curl -X POST https://YOUR-APP.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'
```
Expected response:
```json
{
  "status": "error",
  "error": "Task title is required."
}
```
HTTP Status: `400 Bad Request`.

---

## 🛠️ PART 5: Troubleshooting Common Deployment Issues

### 1. 500 Internal Server Error on Vercel
- **Symptom**: Navigating to `/` displays the custom 500 Internal Server Error page, but `/about` loads fine (200 OK).
- **Cause**: Vercel executes serverless functions in a read-only environment (`/var/task`). If the app still tries to open `tasks.db` in the project root, SQLite throws `sqlite3.OperationalError: attempt to write a readonly database` while creating tables or seeding data.
- **Solution**:
  1. In `config.py`, verify `DATABASE` points to `/tmp/tasks.db` when `VERCEL` is set:
     ```python
     if os.environ.get("VERCEL"):
         DATABASE = os.environ.get("DATABASE", os.path.join(tempfile.gettempdir(), "tasks.db"))
     ```
  2. In `database.py`, ensure `get_db()` automatically creates the parent directory and calls `_init_schema(conn)` when the DB file is missing.
  3. Check the Vercel project settings and verify `VERCEL=1` is present; do not keep a writable SQLite file in the repo root.

### 2. Seeing Blank Tasks After Cold Starts on Vercel
- **Symptom**: Tasks created previously disappear after 15–30 minutes of inactivity.
- **Cause**: Serverless containers are ephemeral. Files written to `/tmp` are wiped when the container spins down.
- **Solution**: For true data persistence, deploy to **Render** (Part 2) where Gunicorn runs with persistent local storage, or connect Flask to a hosted cloud database (e.g., PostgreSQL on Neon/Supabase).

### 3. Missing Error Details in Production
- **Symptom**: In production (`FLASK_DEBUG=False`), error traceback is suppressed for security.
- **Solution**: Check runtime logs in your hosting provider:
  - On Vercel: Dashboard &rarr; Project &rarr; **Logs** (or `vercel logs`).
  - On Render: Dashboard &rarr; Web Service &rarr; **Logs**.
  Our `app.py` error handler logs errors with `app.logger.error(..., exc_info=True)` to ensure stack traces appear in host logs.
