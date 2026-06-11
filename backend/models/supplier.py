"""
Supplier model.

Factory for building a supplier document dict from Flask form data.
"""

from firebase_admin import firestore


def supplier_from_form(form) -> dict:
    """
    Build a supplier data dict from a Flask request.form object.

    Args:
        form: Flask request.form

    Returns:
        dict suitable for Firestore storage.
    """
    return {
        "name": form.get("name", "").strip(),
        "contact_person": form.get("contact_person", "").strip(),
        "email": form.get("email", "").strip(),
        "phone": form.get("phone", "").strip(),
        "address": form.get("address", "").strip(),
        "tax_id": form.get("tax_id", "").strip(),
        "payment_terms": form.get("payment_terms", "").strip(),
        "notes": form.get("notes", "").strip(),
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }
