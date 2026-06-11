"""
User repository — all Firestore operations for the 'users' collection.
"""

import logging
from database.repositories.base_repository import BaseRepository
from database import db

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Handles all reads and writes for the 'users' Firestore collection."""

    collection_name = "users"

    def get_by_uid(self, uid: str) -> dict | None:
        """Fetch a user document by Firebase Auth UID (== Firestore document ID)."""
        return self.get_by_id(uid)

    def get_by_email(self, email: str) -> dict | None:
        """Find the first user document matching the given email address."""
        if db is None:
            return None
        try:
            from google.cloud.firestore import FieldFilter
            docs = (
                self._collection_ref()
                .where(filter=FieldFilter("email", "==", email))
                .limit(1)
                .stream()
            )
            for doc in docs:
                return {"id": doc.id, **(doc.to_dict() or {})}
            return None
        except Exception as exc:
            logger.error("[users] get_by_email error: %s", exc)
            return None

    def provision(self, uid: str, data: dict) -> bool:
        """Create or merge a user profile document keyed by UID."""
        return self.set(uid, data, merge=True)

    def touch_last_login(self, uid: str) -> bool:
        """Update only the last_login_at timestamp for the given user."""
        from firebase_admin import firestore as fs
        return self.update(uid, {"last_login_at": fs.SERVER_TIMESTAMP})


# Module-level singleton
user_repo = UserRepository()
