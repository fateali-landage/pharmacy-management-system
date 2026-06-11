"""
Auth service — Firebase token verification and user session management.

Handles:
  - Verifying a Firebase ID token (Admin SDK first, google-auth fallback)
  - Provisioning new users in Firestore on first login
  - Building the Flask session user dict

No Flask route logic lives here.
"""

import os
import json
import base64
import logging
from typing import Tuple

import firebase_admin

from firebase_admin import auth
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from backend.models.user import user_profile_from_token, session_user_from_data
from database.repositories.user_repository import user_repo

logger = logging.getLogger(__name__)


def _decode_token_payload(id_token: str) -> dict:
    """
    Decode (but NOT verify) the JWT payload for logging purposes only.
    Never use this for authorisation decisions.
    """
    try:
        _, payload_b64, _ = id_token.split(".")
        payload_b64 += "=" * (-len(payload_b64) % 4)
        return json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())
    except Exception:
        return {}


def verify_firebase_token(id_token: str) -> Tuple[str | None, dict | None]:
    """
    Verify a Firebase ID token and return (uid, decoded_token).

    Tries the Admin SDK first; falls back to google-auth library.

    Returns:
        (uid, decoded_token) on success
        (None, None) on failure
    """
    # --- Pre-flight Check ---
    if not firebase_admin._apps:
        logger.warning(
            "[auth_service] Firebase Admin SDK is NOT initialized. "
            "Skipping Admin SDK verification. Will fall back to google-auth library."
        )

    # Firebase Admin SDK only allows clock_skew_seconds between 0 and 60
    clock_skew = min(60, max(0, int(os.environ.get("AUTH_CLOCK_SKEW_SECONDS", "60"))))

    # --- Preview token claims for debugging (non-fatal) ---
    preview = _decode_token_payload(id_token)
    logger.debug(
        "[auth_service] Token preview — aud=%s, iss=%s, sub=%s",
        preview.get("aud"), preview.get("iss"), preview.get("sub"),
    )

    # 1) Admin SDK (only if initialized)
    if firebase_admin._apps:
        try:
            decoded = auth.verify_id_token(id_token, clock_skew_seconds=clock_skew)
            uid = decoded.get("uid") or decoded.get("sub")
            if uid:
                logger.info("[auth_service] Token verified via Admin SDK for uid=%s", uid)
                return uid, decoded
        except Exception as admin_err:
            logger.warning("[auth_service] Admin SDK verification failed: %s", admin_err)

    # 2) google-auth fallback
    try:
        aud = (
            os.environ.get("FIREBASE_PROJECT_ID")
            or os.environ.get("GCLOUD_PROJECT")
            or preview.get("aud")
        )
        req = google_requests.Request()
        try:
            decoded = google_id_token.verify_firebase_token(
                id_token, req, audience=aud, clock_skew_in_seconds=clock_skew
            )
        except TypeError:
            # Older google-auth without clock_skew_in_seconds support
            decoded = google_id_token.verify_firebase_token(id_token, req, audience=aud)

        uid = decoded.get("uid") or decoded.get("sub")
        if uid:
            logger.info("[auth_service] Token verified via google-auth for uid=%s", uid)
            return uid, decoded
    except Exception as fallback_err:
        logger.exception("[auth_service] google-auth fallback failed")

    return None, None


def get_or_provision_user(uid: str, decoded_token: dict) -> dict:
    """
    Fetch an existing Firestore user profile, or create one on first login.

    Args:
        uid:           Firebase Auth UID.
        decoded_token: The verified ID token claims dict.

    Returns:
        The user profile dict (from Firestore or freshly provisioned).
        Falls back to a minimal in-memory dict when Firestore is unavailable.
    """
    existing = user_repo.get_by_uid(uid)

    if existing is None:
        # First login — provision a new profile
        profile = user_profile_from_token(decoded_token)
        user_repo.provision(uid, profile)
        logger.info("[auth_service] Provisioned new user uid=%s", uid)
        return profile

    # Update last_login_at for returning users
    user_repo.touch_last_login(uid)
    return existing


def build_session_user(uid: str, user_data: dict) -> dict:
    """
    Return the compact user dict stored in the Flask session.

    Args:
        uid:       Firebase Auth UID.
        user_data: Full user profile dict.
    """
    return session_user_from_data(uid, user_data)
