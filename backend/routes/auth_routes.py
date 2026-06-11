"""
Auth routes — login, signup, logout, token verification.

Routes are intentionally thin: they parse the request, delegate to
`auth_service`, and return an HTTP response.
"""

import logging
from flask import (
    Blueprint, render_template, redirect, url_for,
    session, request, jsonify, make_response,
)
from firebase_admin import auth

from backend.services.auth_service import verify_firebase_token, get_or_provision_user, build_session_user

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    """Display the login page (or redirect to dashboard if already authenticated)."""
    if "user" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("auth/login.html")


@auth_bp.route("/signup")
def signup():
    """Display the sign-up page (or redirect to dashboard if already authenticated)."""
    if "user" in session:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("auth/signup.html")


@auth_bp.route("/logout")
def logout():
    """Clear the user session and redirect to the login page."""
    session.pop("user", None)
    return redirect(url_for("auth.login"))


@auth_bp.route("/verify-token", methods=["POST", "OPTIONS"])
def verify_token():
    """
    Verify a Firebase ID token POSTed as JSON { "token": "<id_token>" }.

    On success: stores user info in session and returns JSON { success: true, user: {...} }.
    On failure: returns an appropriate 4xx/5xx error.
    """
    # Handle CORS pre-flight
    if request.method == "OPTIONS":
        response = make_response()
        origin = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    try:
        id_token = (request.json or {}).get("token")
        if not id_token:
            return jsonify({"error": "No token provided"}), 400

        uid, decoded_token = verify_firebase_token(id_token)
        if not uid:
            return jsonify({"error": "Authentication failed"}), 401

        user_data = get_or_provision_user(uid, decoded_token)
        session_user = build_session_user(uid, user_data)

        session.permanent = True
        session["user"] = session_user

        origin = request.headers.get("Origin", "*")
        response = jsonify({"success": True, "user": session_user})
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    except auth.ExpiredIdTokenError as exc:
        logger.warning("[auth] Token expired: %s", exc)
        return jsonify({"error": "Token expired"}), 401
    except auth.InvalidIdTokenError as exc:
        logger.warning("[auth] Invalid token: %s", exc)
        return jsonify({"error": "Invalid token"}), 401
    except Exception as exc:
        logger.exception("[auth] Unexpected error in verify_token: %s", exc)
        return jsonify({"error": "Authentication failed"}), 500
