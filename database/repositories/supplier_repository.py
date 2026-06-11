"""
Supplier repository — all Firestore operations for the 'suppliers' collection.
"""

import logging
from database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SupplierRepository(BaseRepository):
    """Handles all reads and writes for the 'suppliers' Firestore collection."""

    collection_name = "suppliers"


# Module-level singleton
supplier_repo = SupplierRepository()
