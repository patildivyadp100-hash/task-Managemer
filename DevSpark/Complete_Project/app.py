"""
=============================================================================
app.py — Main Application Entry Point (Modules 10, 18, 19, 21, 23, 25)
=============================================================================
This is the central entry point that ties together:
  - Configuration (config.py)
  - SQLite Database tables initialization (database.py)
  - Modular Blueprints (routes/task_routes.py, routes/user_routes.py)
  - Global Exception and Error Handlers (Module 21)
  - Production WSGI deployment server compatibility (Gunicorn on Render)

Modules Covered:
  - Module 10: Introduction to Flask & App creation
  - Module 18: SQLite Initialization on startup
  - Module 19: Blueprint Registration & Architectural Separation
  - Module 21: Validation & Global Error Handlers (404, 400, 500)
  - Module 23: Production Readiness
  - Module 25: Render Deployment (entry point for gunicorn app:app)
=============================================================================
"""

from flask import Flask, jsonify, render_template, request
from config import Config
from database import init_db
from routes import task_bp, user_bp


def create_app(config_class=Config):
    """
    Application Factory pattern:
    Creates and configures a Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLite database schema within application context
    with app.app_context():
        init_db()

    # Register modular Blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)

    # Register central error handlers
    register_error_handlers(app)

    return app


def register_error_handlers(app):
    """
    Module 21: Centralized Error Handlers
    Distinguishes between API clients (JSON) and Web browsers (HTML).
    """

    def is_api_client():
        return (
            request.path.startswith("/api/")
            or request.headers.get("Accept") == "application/json"
            or request.is_json
        )

    @app.errorhandler(400)
    def bad_request_error(error):
        if is_api_client():
            return jsonify({
                "status": "error",
                "error": "Bad request. Please verify the request parameters or body."
            }), 400
        return render_template("404.html", message="Bad Request (400)"), 400

    @app.errorhandler(404)
    def not_found_error(error):
        if is_api_client():
            return jsonify({
                "status": "error",
                "error": "Resource not found on this server."
            }), 404
        return render_template("404.html", message="Page Not Found (404)"), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal Server Error: {error}", exc_info=True)
        if is_api_client():
            return jsonify({
                "status": "error",
                "error": "An internal server error occurred."
            }), 500
        return render_template("500.html"), 500


# Application instance for both local execution and Gunicorn (Module 25: gunicorn app:app)
app = create_app()


if __name__ == "__main__":
    # Local development server
    # Debug mode is loaded from Config (FLASK_DEBUG environment variable)
    app.run(debug=app.config.get("DEBUG", True), port=5000)
