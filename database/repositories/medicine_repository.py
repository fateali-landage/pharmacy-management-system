"""
Medicine repository — all Firestore operations for the 'medicines' collection.
"""

import logging
from database.repositories.base_repository import BaseRepository, FieldFilter
from database import db

logger = logging.getLogger(__name__)


class MedicineRepository(BaseRepository):
    """Handles all reads and writes for the 'medicines' Firestore collection."""

    collection_name = "medicines"

    def get_with_stock(self) -> list:
        """Return only medicines that have stock > 0, ordered by name.

        NOTE: Fetches all medicines client-side and filters/sorts in memory.
        This avoids a Firestore composite index requirement on (stock ASC, name ASC).
        For large collections, create the composite index in Firebase Console instead.
        """
        if db is None:
            return []
        try:
            # Fetch all and filter client-side to avoid composite index requirement
            all_docs = self._collection_ref().stream()
            results = []
            for d in all_docs:
                data = d.to_dict() or {}
                try:
                    stock = int(data.get("stock", 0))
                except (TypeError, ValueError):
                    stock = 0
                if stock > 0:
                    results.append({"id": d.id, **data})
            # Sort by name client-side
            results.sort(key=lambda x: (x.get("name") or "").lower())
            return results
        except Exception as exc:
            logger.error("[medicines] get_with_stock error: %s", exc)
            return []

    def get_expiring_before(self, horizon_date) -> list:
        """Return medicines expiring on or before the given date."""
        # NOTE: Firestore date filtering requires the field to be a Timestamp.
        # The dashboard service does client-side filtering for flexibility.
        return self.get_all()


# Module-level singleton — import this in services
medicine_repo = MedicineRepository()
