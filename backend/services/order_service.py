"""
Order service — business logic for the orders module.

Computes per-order stats and handles order creation.
"""

import logging
from datetime import datetime, timezone, timedelta

from backend.utils.helpers import parse_amount
from backend.models.order import order_from_form
from database.repositories.order_repository import order_repo

logger = logging.getLogger(__name__)

# Statuses considered "pending" across EN and AR
PENDING_STATUSES = ["pending", "قيد الانتظار"]


def get_orders_with_stats() -> tuple[list, dict]:
    """
    Fetch recent orders and compute summary statistics.

    Returns:
        (orders_list, stats_dict)

        stats keys:
          - total_orders      (int)
          - pending           (int)
          - month_total       (float)
          - avg_order_value   (float | None)
    """
    stats = {
        "total_orders": 0,
        "pending": 0,
        "month_total": 0.0,
        "avg_order_value": None,
    }

    try:
        orders = order_repo.get_recent(limit=50)

        now = datetime.now(timezone.utc)
        start_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        next_month = (start_month.replace(day=28) + timedelta(days=4)).replace(day=1)

        total_sum = 0.0
        total_count = 0

        all_orders = order_repo.get_all()
        for doc in all_orders:
            stats["total_orders"] += 1

            st = doc.get("status", "")
            if isinstance(st, str):
                st_l = st.lower()
                if "pend" in st_l or st in PENDING_STATUSES:
                    stats["pending"] += 1

            amt = parse_amount(doc.get("total"))
            if amt is not None:
                total_sum += amt
                total_count += 1

                # Month total
                created = doc.get("date")
                if isinstance(created, datetime):
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    if start_month <= created < next_month:
                        stats["month_total"] += amt

        if total_count > 0:
            stats["avg_order_value"] = round(total_sum / total_count, 2)

    except Exception as exc:
        logger.error("[order_service] get_orders_with_stats error: %s", exc)
        orders = []

    return orders, stats


def create_order(form, session_user: dict) -> bool:
    """
    Persist a new order from form data.

    Returns True on success, False on failure.
    """
    data = order_from_form(form, session_user)
    doc_id = order_repo.add(data)
    if doc_id:
        logger.info("[order_service] Created order id=%s by %s", doc_id, session_user.get("email"))
        return True
    logger.error("[order_service] Failed to create order")
    return False


def delete_order(doc_id: str) -> bool:
    """Delete an order document by its doc_id."""
    success = order_repo.delete(doc_id)
    if success:
        logger.info("[order_service] Deleted order id=%s", doc_id)
        return True
    logger.error("[order_service] Failed to delete order id=%s", doc_id)
    return False
