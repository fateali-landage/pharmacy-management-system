"""
Order repository — all Firestore operations for the 'orders' collection.
"""

import logging
from datetime import datetime, timezone
from database.repositories.base_repository import BaseRepository, FieldFilter
from database import db

logger = logging.getLogger(__name__)


class OrderRepository(BaseRepository):
    """Handles all reads and writes for the 'orders' Firestore collection."""

    collection_name = "orders"

    def get_recent(self, limit: int = 50) -> list:
        """Return the most recent orders ordered by date descending."""
        if db is None:
            return []
        try:
            docs = (
                self._collection_ref()
                .order_by("date", direction="DESCENDING")
                .limit(limit)
                .stream()
            )
            return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
        except Exception as exc:
            logger.error("[orders] get_recent error: %s", exc)
            return []

    def get_by_status(self, statuses: list) -> list:
        """Return orders whose status field is in the given list."""
        if db is None:
            return []
        try:
            docs = (
                self._collection_ref()
                .where(filter=FieldFilter("status", "in", statuses))
                .stream()
            )
            return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
        except Exception as exc:
            logger.error("[orders] get_by_status error: %s", exc)
            return []

    def get_in_date_range(self, start_dt: datetime, end_dt: datetime) -> list:
        """Return orders whose date falls within [start_dt, end_dt)."""
        if db is None:
            return []
        try:
            # Use chained .where() calls with FieldFilter — the correct modern approach.
            docs = (
                self._collection_ref()
                .where(filter=FieldFilter("date", ">=", start_dt))
                .where(filter=FieldFilter("date", "<", end_dt))
                .stream()
            )
            return [{"id": d.id, **(d.to_dict() or {})} for d in docs]
        except Exception as exc:
            logger.warning("[orders] get_in_date_range fell back to full scan: %s", exc)
            # Client-side filter as last resort
            all_orders = self.get_all()
            result = []
            for order in all_orders:
                dt = order.get("date")
                if not isinstance(dt, datetime):
                    continue
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if start_dt <= dt < end_dt:
                    result.append(order)
            return result


# Module-level singleton
order_repo = OrderRepository()
