"""
Shared helper / utility functions.

These are pure-Python helpers used by multiple services. Keeping them here
avoids duplicating the same parsing logic across the codebase.
"""

from datetime import datetime


# ---------------------------------------------------------------------------
# Amount / currency parsing
# ---------------------------------------------------------------------------

def parse_amount(value) -> float | None:
    """
    Coerce a Firestore field value to a float amount.

    Accepts:
    - int / float  → returned directly
    - str          → non-numeric characters stripped, then converted
    - None         → returns None

    Returns None when conversion is not possible.

    Examples::

        parse_amount(42)          # 42.0
        parse_amount("1,234.56")  # 1234.56
        parse_amount("DZD 200")   # 200.0
        parse_amount(None)        # None
        parse_amount("N/A")       # None
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = "".join(ch for ch in value if ch.isdigit() or ch in (".", ","))
        cleaned = cleaned.replace(",", "")
        try:
            return float(cleaned) if cleaned else None
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

def parse_date(value) -> datetime | None:
    """
    Coerce a Firestore field value to a datetime object.

    Accepts:
    - datetime  → returned directly
    - str       → parsed with strptime (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    - None      → returns None

    Returns None when parsing fails.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(value[:len(fmt)], fmt)
            except ValueError:
                continue
    return None


# ---------------------------------------------------------------------------
# Integer parsing
# ---------------------------------------------------------------------------

def safe_int(value, default: int = 0) -> int:
    """
    Safely convert a value to int, returning *default* on failure.

    Examples::

        safe_int("50")   # 50
        safe_int(None)   # 0
        safe_int("abc")  # 0
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
