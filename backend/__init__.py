"""
Flask application factory.

`create_app()` is the single entry point for building the Flask application.
It wires together:
  - Configuration (from environment + config.py)
  - CORS
  - Context processors (translations, g.lang, g.now)
  - All route blueprints
  - Request lifecycle hooks

Usage::

    from backend import create_app
    app = create_app()
"""

import os
import logging
from datetime import datetime

from flask import Flask, session, request, g, make_response
from flask_cors import CORS
from dotenv import load_dotenv

from backend.utils.translations import get_translation

# Load .env for local development convenience
load_dotenv()

# Configure module-level logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Construct and configure the Flask application.

    Returns:
        A fully configured Flask WSGI application object.
    """
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "static"),
        template_folder=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"),
    )

    # ------------------------------------------------------------------
    # Secret key (must be set via env var in production)
    # ------------------------------------------------------------------
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    if app.secret_key == "dev-secret-change-me":
        logger.warning(
            "FLASK_SECRET_KEY is not set — using insecure default. "
            "Set it in your environment before deploying."
        )

    # ------------------------------------------------------------------
    # Session cookie settings (dev vs. production)
    # ------------------------------------------------------------------
    _env = os.environ.get("FLASK_ENV") or os.environ.get("ENV")
    _is_dev = (_env == "development") or (os.environ.get("FLASK_DEBUG") == "1")

    if _is_dev:
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["SESSION_COOKIE_SECURE"] = False
    else:
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True

    # Firebase web config — read from env so keys are never hardcoded in JS
    app.config["FIREBASE_API_KEY"] = os.environ.get("FIREBASE_API_KEY", "")
    app.config["FIREBASE_AUTH_DOMAIN"] = os.environ.get("FIREBASE_AUTH_DOMAIN", "")
    app.config["FIREBASE_PROJECT_ID"] = os.environ.get("FIREBASE_PROJECT_ID", "")
    app.config["FIREBASE_STORAGE_BUCKET"] = os.environ.get("FIREBASE_STORAGE_BUCKET", "")
    app.config["FIREBASE_MESSAGING_SENDER_ID"] = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "")
    app.config["FIREBASE_APP_ID"] = os.environ.get("FIREBASE_APP_ID", "")
    app.config["FIREBASE_MEASUREMENT_ID"] = os.environ.get("FIREBASE_MEASUREMENT_ID", "")

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
            "supports_credentials": True,
        }
    })

    # ------------------------------------------------------------------
    # Request lifecycle hooks
    # ------------------------------------------------------------------
    @app.before_request
    def _before_request():
        """Set language and translation helper on Flask's g object."""
        # English is the only supported language.
        g.lang = "en"
        session["language"] = "en"
        g._ = lambda key: get_translation(key, "en")
        g.now = datetime.now()

    # ------------------------------------------------------------------
    # Jinja2 context processors
    # ------------------------------------------------------------------
    @app.context_processor
    def _inject_globals():
        """Inject translation helper, gettext alias, and now into all templates."""
        return {
            "_": lambda key: get_translation(key, "en"),
            "gettext": lambda key: get_translation(key, "en"),
            "now": datetime.now(),
        }

    # ------------------------------------------------------------------
    # Register all blueprints
    # ------------------------------------------------------------------
    from backend.routes import register_all
    register_all(app)

    logger.info("Flask application created successfully")
    return app
