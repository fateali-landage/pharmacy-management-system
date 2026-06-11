"""
COMPATIBILITY SHIM — firebase_client.py (root)

This file is kept for backwards compatibility only.
The canonical Firebase client module has moved to:
    database/firebase_client.py

All Firebase Admin SDK initialization is handled by database/firebase_config.py.
Do NOT call firebase_admin.initialize_app() here — it conflicts with the
canonical initialization and causes token verification failures (HTTP 401).

Please update any imports to use the new location.
"""

from database.firebase_client import get_collection, add_document, USE_FIREBASE, MOCK

__all__ = ["get_collection", "add_document", "USE_FIREBASE", "MOCK"]
