"""
User model.

Helper for constructing user profile dicts used in session and Firestore.
"""

from firebase_admin import firestore


def user_profile_from_token(decoded_token: dict) -> dict:
    """
    Build a minimal user profile dict from a decoded Firebase ID token.

    Used when provisioning a new user in Firestore.
    """
    email = decoded_token.get("email", "")
    default_name = (
        decoded_token.get("name")
        or email.split("@")[0]
        or "User"
    )
    return {
        "email": email,
        "name": default_name,
        "role": "user",
        "created_at": firestore.SERVER_TIMESTAMP,
        "last_login_at": firestore.SERVER_TIMESTAMP,
    }


def session_user_from_data(uid: str, user_data: dict) -> dict:
    """
    Build the compact user dict stored in Flask session.

    Only essential fields are persisted in the session cookie.
    """
    return {
        "uid": uid,
        "email": user_data.get("email", ""),
        "name": user_data.get("name", "User"),
        "role": user_data.get("role", "user"),
    }
