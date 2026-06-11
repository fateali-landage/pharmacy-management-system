"""
Inventory repository — all Firestore operations for the 'inventory' collection.
"""

import logging
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class InventoryRepository(BaseRepository):
    """Handles all reads and writes for the 'inventory' Firestore collection."""

    collection_name = "medicines"


# Module-level singleton
inventory_repo = InventoryRepository()
