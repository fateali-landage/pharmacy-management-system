"""
Order model.

Factory for building a purchase order dict from Flask form data.
"""

from firebase_admin import firestore


def order_from_form(form, session_user: dict) -> dict:
    """
    Build an order data dict from a Flask request.form object.

    Args:
        form:         Flask request.form
        session_user: The current user dict from Flask session.

    Returns:
        dict suitable for Firestore storage.
    """
    supplier = form.get("supplier") or form.get("supplier_text", "")

    item_ids = form.getlist("item_id[]")
    quantities = form.getlist("quantity[]")

    items = []
    for item_id, qty in zip(item_ids, quantities):
        try:
            quantity = int(qty)
        except (TypeError, ValueError):
            quantity = 0
        if item_id:
            items.append({"item_id": item_id, "quantity": quantity})

    return {
        "supplier": supplier.strip(),
        "items": items,
        "status": "pending",
        "created_by": session_user.get("email", ""),
        "date": firestore.SERVER_TIMESTAMP,
    }
