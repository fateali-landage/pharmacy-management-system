"""
Supplier service — business logic for the suppliers module.

Computes supplier statistics (active orders, monthly expenses, delivery times)
and handles supplier creation.
"""

import logging
from datetime import datetime, timezone, timedelta

from backend.utils.helpers import parse_amount
from backend.models.supplier import supplier_from_form
from database.repositories.supplier_repository import supplier_repo
from database.repositories.order_repository import order_repo

logger = logging.getLogger(__name__)

# Statuses that count as "active" orders
ACTIVE_STATUSES = [
    "pending", "processing", "in_transit", "shipped",
    "قيد الانتظار", "قيد المعالجة", "تم الشحن",
]
DELIVERED_STATUSES = ["delivered", "تم التسليم"]


def get_suppliers_with_stats() -> tuple[list, dict]:
    """
    Fetch all suppliers and compute summary statistics.

    Returns:
        (suppliers_list, stats_dict)

        stats keys:
          - total_suppliers    (int)
          - active_orders      (int)
          - expenses_month     (float)
          - avg_delivery_days  (float | None)
    """
    stats = {
        "total_suppliers": 0,
        "active_orders": 0,
        "expenses_month": 0.0,
        "avg_delivery_days": None,
    }

    try:
        suppliers = supplier_repo.get_all()
        stats["total_suppliers"] = len(suppliers)

        # Active order count
        try:
            active_orders = order_repo.get_by_status(ACTIVE_STATUSES)
            stats["active_orders"] = len(active_orders)
        except Exception:
            all_orders = order_repo.get_all()
            stats["active_orders"] = sum(
                1 for o in all_orders
                if _is_active_order(o.get("status", ""))
            )

        # Monthly expenses
        now = datetime.now(timezone.utc)
        start_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        next_month = (start_month.replace(day=28) + timedelta(days=4)).replace(day=1)

        try:
            month_orders = order_repo.get_in_date_range(start_month, next_month)
        except Exception:
            month_orders = order_repo.get_all()

        total_sum = 0.0
        for order in month_orders:
            amt = parse_amount(order.get("total"))
            if amt is not None:
                total_sum += amt
        stats["expenses_month"] = round(total_sum, 2)

        # Average delivery time
        try:
            delivered = order_repo.get_by_status(DELIVERED_STATUSES)
            times = []
            for d in delivered:
                created = d.get("date")
                delivered_at = d.get("delivered_at")
                if (
                    created and delivered_at
                    and hasattr(delivered_at, "timestamp")
                    and hasattr(created, "timestamp")
                ):
                    delta = delivered_at - created
                    times.append(delta.total_seconds() / 86400.0)
            if times:
                stats["avg_delivery_days"] = round(sum(times) / len(times), 1)
        except Exception:
            pass

    except Exception as exc:
        logger.error("[supplier_service] get_suppliers_with_stats error: %s", exc)
        suppliers = []

    return suppliers, stats


def add_supplier(form) -> bool:
    """
    Persist a new supplier from form data.

    Returns True on success, False on failure.
    """
    data = supplier_from_form(form)
    # Use set() with auto-generated ID via add()
    doc_id = supplier_repo.add(data)
    if doc_id:
        logger.info("[supplier_service] Added supplier '%s' id=%s", data.get("name"), doc_id)
        return True
    logger.error("[supplier_service] Failed to add supplier '%s'", data.get("name"))
    return False


def get_supplier_by_id(doc_id: str) -> dict | None:
    """Retrieve a single supplier by its doc_id."""
    return supplier_repo.get_by_id(doc_id)


def update_supplier(doc_id: str, form) -> bool:
    """Update an existing supplier document using form data."""
    data = supplier_from_form(form)
    success = supplier_repo.update(doc_id, data)
    if success:
        logger.info("[supplier_service] Updated supplier '%s' (id=%s)", data.get("name"), doc_id)
        return True
    logger.error("[supplier_service] Failed to update supplier '%s' (id=%s)", data.get("name"), doc_id)
    return False


def delete_supplier(doc_id: str) -> bool:
    """Delete a supplier document by its doc_id."""
    success = supplier_repo.delete(doc_id)
    if success:
        logger.info("[supplier_service] Deleted supplier id=%s", doc_id)
        return True
    logger.error("[supplier_service] Failed to delete supplier id=%s", doc_id)
    return False


def _is_active_order(status: str) -> bool:
    if not isinstance(status, str):
        return False
    sl = status.lower()
    return any(k in sl for k in ("pend", "process", "ship")) or status in ACTIVE_STATUSES
