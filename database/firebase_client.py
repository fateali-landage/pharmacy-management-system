"""
Firebase client wrapper.

Provides a thin abstraction over the Firestore `db` object with a mock
fallback for local development when Firebase credentials are not configured.

Usage:
    from database.firebase_client import get_db, USE_FIREBASE, MOCK
"""

from database import db

# True when the Firebase Admin SDK was successfully initialised
USE_FIREBASE: bool = db is not None

# ---------------------------------------------------------------------------
# Mock data — used as an in-process fallback when Firebase is unavailable.
# This lets developers run the app locally without credentials.
# ---------------------------------------------------------------------------
MOCK: dict = {
    "inventory": [
        {
            "name": "Pain Relief Tablets",
            "batch": "BTCH2023001",
            "qty": 500,
            "expiry": "2024-12-31",
            "status": "Adequate",
        },
        {
            "name": "Antibiotic Capsules",
            "batch": "BTCH2023002",
            "qty": 75,
            "expiry": "2024-06-30",
            "status": "Low Stock",
        },
    ],
    "medicines": [
        {
            "name": "Medication A",
            "category": "Pain Relief",
            "stock": 150,
            "expiry": "2024-12-31",
        },
        {
            "name": "Medication B",
            "category": "Antibiotics",
            "stock": 25,
            "expiry": "2024-08-15",
        },
    ],
    "orders": [
        {
            "id": "#ORD12345",
            "supplier": "MediCorp Inc.",
            "date": "2023-08-15",
            "status": "Completed",
        },
        {
            "id": "#ORD12346",
            "supplier": "HealthPlus Supplies",
            "date": "2023-08-16",
            "status": "In Transit",
        },
    ],
    "suppliers": [],
    "reports": [],
    "users": [],
    "stats": {
        "total_medicines": 1250,
        "expiring_soon": 35,
        "active_prescriptions": 120,
        "low_inventory": 15,
    },
}


def get_db():
    """Return the live Firestore client, or None if not configured."""
    return db


def get_collection(name: str) -> list:
    """
    Return all documents from a Firestore collection as a list of dicts.
    Falls back to MOCK data when Firebase is not configured.
    """
    if USE_FIREBASE:
        try:
            docs = db.collection(name).stream()
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception:
            return MOCK.get(name, [])
    return MOCK.get(name, [])


def add_document(collection: str, data: dict):
    """
    Add a document to a Firestore collection.
    Falls back to appending to MOCK data when Firebase is not configured.

    Returns the new document ID on success, or False on failure.
    """
    if USE_FIREBASE:
        try:
            result = db.collection(collection).add(data)
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
        except Exception:
            return False
    # Mock write
    if collection in MOCK and isinstance(MOCK[collection], list):
        MOCK[collection].append(data)
        return True
    return False
