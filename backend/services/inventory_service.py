"""
Inventory service — business logic for the inventory module.

Computes per-item and aggregate inventory statistics.
"""

import logging

from backend.utils.helpers import parse_amount, safe_int
from database.repositories.inventory_repository import inventory_repo
from database.repositories.order_repository import order_repo

logger = logging.getLogger(__name__)

# Statuses that indicate an item is "on order"
ON_ORDER_STATUSES = [
    "pending", "processing", "in_transit",
    "قيد الانتظار", "قيد المعالجة",
]


def get_inventory_with_stats() -> tuple[list, dict]:
    """
    Fetch all inventory items and compute aggregate stats.

    Returns:
        (items_list, inv_stats_dict)

        inv_stats keys:
          - total_items, active_items, low_stock, critical,
            out_of_stock, on_order, inventory_value,
            active_pct, low_pct, on_order_pct
    """
    inv_stats = {
        "total_items": 0,
        "active_items": 0,
        "low_stock": 0,
        "critical": 0,
        "out_of_stock": 0,
        "on_order": 0,
        "inventory_value": 0.0,
        "active_pct": 0,
        "low_pct": 0,
        "on_order_pct": 0,
    }

    try:
        items = inventory_repo.get_all()
        inv_stats["total_items"] = len(items)

        total_value = 0.0
        low_count = 0
        critical_count = 0
        active_count = 0
        out_count = 0

        for it in items:
            stock = safe_int(it.get("stock"), 0)
            price = parse_amount(it.get("price"))

            if price is not None:
                total_value += price * stock

            min_val = it.get("min")
            try:
                min_i = int(min_val) if min_val is not None and str(min_val) != "" else None
            except (TypeError, ValueError):
                min_i = None

            if stock > 0 and it.get("active", True) is not False:
                active_count += 1
            if stock <= 0:
                out_count += 1
            if min_i is not None and stock < min_i:
                low_count += 1
                threshold = max(min_i // 2, 1)
                if stock < threshold:
                    critical_count += 1

        inv_stats["inventory_value"] = round(total_value, 2)
        inv_stats["low_stock"] = low_count
        inv_stats["critical"] = critical_count
        inv_stats["active_items"] = active_count
        inv_stats["out_of_stock"] = out_count

        # On-order: count distinct item IDs referenced in pending/processing orders
        try:
            pending_orders = order_repo.get_by_status(ON_ORDER_STATUSES)
        except Exception:
            pending_orders = order_repo.get_all()

        on_order_ids: set = set()
        for order in pending_orders:
            for row in (order.get("items") or []):
                if isinstance(row, dict):
                    iid = row.get("item_id") or row.get("id") or row.get("code")
                    if iid:
                        on_order_ids.add(str(iid))
        inv_stats["on_order"] = len(on_order_ids)

        # Percentage breakdowns (for progress bars)
        total = inv_stats["total_items"]
        if total > 0:
            inv_stats["active_pct"] = round((active_count / total) * 100)
            inv_stats["low_pct"] = round((low_count / total) * 100)
            inv_stats["on_order_pct"] = round((len(on_order_ids) / total) * 100)

    except Exception as exc:
        logger.error("[inventory_service] get_inventory_with_stats error: %s", exc)
        items = []

    return items, inv_stats
