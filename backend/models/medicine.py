"""
Medicine model.

Defines the canonical fields and a factory method for building a medicine
document dict from a Flask form submission.
"""

from backend.utils.helpers import safe_int


# Fields expected in every Medicine Firestore document
MEDICINE_FIELDS = ("name", "category", "stock", "expiry", "price")


def medicine_from_form(form) -> dict:
    """
    Build a medicine data dict from a Flask request.form object.

    Args:
        form: Flask request.form (ImmutableMultiDict)

    Returns:
        dict suitable for Firestore storage.
    """
    from backend.utils.helpers import parse_amount
    price_val = parse_amount(form.get("price"))
    if price_val is None:
        price_val = 0.0
    return {
        "name": form.get("name", "").strip(),
        "category": form.get("category", "").strip(),
        "stock": safe_int(form.get("stock"), default=0),
        "expiry": form.get("expiry", "").strip(),
        "price": price_val,
    }
