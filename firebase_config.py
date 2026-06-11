"""
COMPATIBILITY SHIM — firebase_config.py (root)

This file is kept for backwards compatibility only.
The canonical Firebase config module has moved to:
    database/firebase_config.py

Please update any imports to use the new location.
"""

from database.firebase_config import initialize_firebase, _build_credential

__all__ = ["initialize_firebase", "_build_credential"]
