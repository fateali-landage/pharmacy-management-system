"""
Base repository — generic Firestore CRUD operations.

All domain-specific repositories inherit from BaseRepository, which
handles the common pattern of streaming a collection, fetching a single
document, adding, updating, and deleting documents.

No route or service should import `db` directly — always go through a repository.
"""

import logging
from database import db

from google.cloud.firestore import FieldFilter

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    Generic Firestore repository.

    Subclasses set `collection_name` to the Firestore collection they manage.
    """

    collection_name: str = ""

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_all(self) -> list:
        """Return every document in the collection as a list of dicts."""
        if db is None:
            logger.warning("[%s] Firestore not initialised — returning []", self.collection_name)
            return []
        try:
            docs = db.collection(self.collection_name).stream()
            return [{"id": doc.id, **(doc.to_dict() or {})} for doc in docs]
        except Exception as exc:
            logger.error("[%s] get_all error: %s", self.collection_name, exc)
            return []

    def get_by_id(self, doc_id: str) -> dict | None:
        """Fetch a single document by its Firestore ID. Returns None when not found."""
        if db is None:
            return None
        try:
            doc = db.collection(self.collection_name).document(doc_id).get()
            if doc.exists:
                return {"id": doc.id, **(doc.to_dict() or {})}
            return None
        except Exception as exc:
            logger.error("[%s] get_by_id(%s) error: %s", self.collection_name, doc_id, exc)
            return None

    def query_where(self, field: str, op: str, value) -> list:
        """Return documents matching a simple where-clause filter."""
        if db is None:
            return []
        try:
            docs = (
                db.collection(self.collection_name)
                .where(filter=FieldFilter(field, op, value))
                .stream()
            )
            return [{"id": doc.id, **(doc.to_dict() or {})} for doc in docs]
        except Exception as exc:
            logger.error("[%s] query_where error: %s", self.collection_name, exc)
            return []

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def add(self, data: dict) -> str | None:
        """
        Add a new document with auto-generated ID.

        Returns the new document ID on success, or None on failure.
        """
        if db is None:
            logger.warning("[%s] Firestore not initialised — add skipped", self.collection_name)
            return None
        try:
            result = db.collection(self.collection_name).add(data)
            # Find DocumentReference safely from returned result
            doc_ref = None
            if isinstance(result, (tuple, list)):
                import datetime
                for item in result:
                    if hasattr(item, "id") and not isinstance(item, (datetime.datetime, datetime.date)):
                        doc_ref = item
                        break
                if doc_ref is None:
                    for item in result:
                        if hasattr(item, "id"):
                            doc_ref = item
                            break
                if doc_ref is None:
                    doc_ref = result[0]
            else:
                doc_ref = result
            return doc_ref.id
        except Exception as exc:
            logger.error("[%s] add error: %s", self.collection_name, exc)
            return None

    def set(self, doc_id: str, data: dict, merge: bool = False) -> bool:
        """
        Create or overwrite a document with a known ID.

        When merge=True the write is a partial update (same as Firestore merge).
        """
        if db is None:
            return False
        try:
            db.collection(self.collection_name).document(doc_id).set(data, merge=merge)
            return True
        except Exception as exc:
            logger.error("[%s] set(%s) error: %s", self.collection_name, doc_id, exc)
            return False

    def update(self, doc_id: str, data: dict) -> bool:
        """Partially update specific fields of an existing document."""
        if db is None:
            return False
        try:
            db.collection(self.collection_name).document(doc_id).update(data)
            return True
        except Exception as exc:
            logger.error("[%s] update(%s) error: %s", self.collection_name, doc_id, exc)
            return False

    def delete(self, doc_id: str) -> bool:
        """Delete a document by its Firestore ID."""
        if db is None:
            return False
        try:
            db.collection(self.collection_name).document(doc_id).delete()
            return True
        except Exception as exc:
            logger.error("[%s] delete(%s) error: %s", self.collection_name, doc_id, exc)
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _collection_ref(self):
        """Return the raw Firestore CollectionReference for advanced queries."""
        if db is None:
            raise RuntimeError("Firestore client is not initialised")
        return db.collection(self.collection_name)
