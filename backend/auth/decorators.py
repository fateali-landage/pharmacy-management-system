"""
Authentication decorators.

Provides `login_required` to protect Flask routes that need an authenticated
session, and `role_required` for future role-based access control.
"""

import logging
from functools import wraps
from flask import session, redirect, url_for, request, jsonify

logger = logging.getLogger(__name__)


def login_required(f):
    """
    Decorator that ensures the current request has an authenticated session.

    - For regular requests: redirects to the login page if the user is not logged in.
    - For AJAX requests (X-Requested-With: XMLHttpRequest): returns a 401 JSON response.

    Usage::

        @app.route('/dashboard')
        @login_required
        def dashboard():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            logger.debug("Unauthenticated access attempt to %s", request.path)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def role_required(*roles):
    """
    Decorator that restricts access to users whose role is in *roles*.

    Must be applied after @login_required::

        @app.route('/admin')
        @login_required
        @role_required('admin')
        def admin_panel():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get("user", {})
            if user.get("role") not in roles:
                logger.warning(
                    "User %s (role=%s) denied access to %s",
                    user.get("email"),
                    user.get("role"),
                    request.path,
                )
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"error": "Insufficient permissions"}), 403
                return redirect(url_for("dashboard.dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
