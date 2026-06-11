"""
COMPATIBILITY SHIM — translations.py (root)

This file is kept for backwards compatibility only.
The canonical translations module has moved to:
    backend/utils/translations.py

The system now operates in English only. Arabic translations
have been removed.

Please update any imports to use the new location.
"""

from backend.utils.translations import get_translation, _translations

__all__ = ["get_translation", "_translations"]
