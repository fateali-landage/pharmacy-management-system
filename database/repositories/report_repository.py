"""
Report repository — all Firestore operations for the 'reports' collection.
"""

import logging
from database.repositories.base_repository import BaseRepository
from database import db

logger = logging.getLogger(__name__)


class ReportRepository(BaseRepository):
    """Handles all reads and writes for the 'reports' Firestore collection."""

    collection_name = "reports"

    def get_recent(self, limit: int = 10) -> list:
        """Return the most recent reports ordered by created_at or date descending."""
        if db is None:
            return []
        try:
            docs = (
                self._collection_ref()
                .order_by("created_at", direction="DESCENDING")
                .limit(limit)
                .stream()
            )
            return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
        except Exception:
            try:
                # Fallback: order by 'date' field if 'created_at' index is missing
                docs = (
                    self._collection_ref()
                    .order_by("date", direction="DESCENDING")
                    .limit(limit)
                    .stream()
                )
                return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
            except Exception as exc:
                logger.error("[reports] get_recent error: %s", exc)
                return []


# Module-level singleton
report_repo = ReportRepository()
