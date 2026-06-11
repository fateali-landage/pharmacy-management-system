"""
Database layer package.

Exports the Firestore `db` and Cloud Storage `bucket` singletons
that are initialized once at application startup via `firebase_config.initialize_firebase()`.

Usage:
    from database import db, bucket
"""

from database.firebase_config import initialize_firebase

# Initialize once; db / bucket may be None when credentials are absent
db, bucket = initialize_firebase()

__all__ = ["db", "bucket"]
