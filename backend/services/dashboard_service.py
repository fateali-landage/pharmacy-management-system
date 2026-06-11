"""
Dashboard service — computes real-time stats and chart data for the dashboard.

All Firestore interactions go through repository objects.
Business logic (date arithmetic, aggregation) lives here, not in the route.
"""

import calendar
import logging
from datetime import datetime, timezone, timedelta, date

from backend.utils.helpers import parse_amount, safe_int
from database.repositories.medicine_repository import medicine_repo
from database.repositories.order_repository import order_repo
from database.repositories.inventory_repository import inventory_repo
from database import db

from google.cloud.firestore import FieldFilter as _FieldFilter

logger = logging.getLogger(__name__)


def get_dashboard_data() -> dict:
    """
    Compute and return all data needed to render the dashboard template.

    Returns:
        {
            'stats':      { total_medicines, expiring_soon, active_prescriptions, low_inventory }
            'chart_data': { months: [...], sales: [...] }
        }
    """
    stats = {
        "total_medicines": 0,
        "expiring_soon": 0,
        "active_prescriptions": 0,
        "low_inventory": 0,
    }
    chart_data = {"months": [], "sales": []}

    try:
        # ── 1. Medicine count & expiry check ──────────────────────────────
        today = datetime.now(timezone.utc).date()
        horizon = today + timedelta(days=30)

        medicines = medicine_repo.get_all()
        stats["total_medicines"] = len(medicines)

        expiring = 0
        for med in medicines:
            expiry_raw = med.get("expiry") or med.get("expiration")
            exp_date = _parse_expiry_date(expiry_raw)
            if exp_date and today <= exp_date <= horizon:
                expiring += 1
        stats["expiring_soon"] = expiring

        # ── 2. Active prescriptions ───────────────────────────────────────
        stats["active_prescriptions"] = _count_active_prescriptions()

        # ── 3. Low inventory ──────────────────────────────────────────────
        inv_items = inventory_repo.get_all()
        low = sum(
            1 for it in inv_items
            if _is_low_stock(it)
        )
        stats["low_inventory"] = low

        # ── 4. Revenue chart (last 6 months) ──────────────────────────────
        chart_data = _build_chart_data()

    except Exception as exc:
        logger.error("[dashboard_service] Error computing dashboard data: %s", exc)

    return {"stats": stats, "chart_data": chart_data}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _parse_expiry_date(expiry) -> date | None:
    if isinstance(expiry, datetime):
        return expiry.date()
    if isinstance(expiry, str):
        try:
            return datetime.strptime(expiry[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    return None


def _is_low_stock(item: dict) -> bool:
    """Return True when the item's stock is below its minimum threshold."""
    stock = safe_int(item.get("stock"), 0)
    min_val = item.get("min")
    try:
        min_i = int(min_val) if min_val is not None and str(min_val) != "" else None
    except (TypeError, ValueError):
        min_i = None
    return min_i is not None and stock < min_i


def _count_active_prescriptions() -> int:
    """Count prescriptions with an active status. Returns 0 on any error."""
    if db is None:
        return 0
    try:
        active_statuses = ["active", "processing", "قيد التنفيذ"]
        docs = (
            db.collection("prescriptions")
            .where(filter=_FieldFilter("status", "in", active_statuses))
            .stream()
        )
        return sum(1 for _ in docs)
    except Exception:
        try:
            docs = db.collection("prescriptions").stream()
            count = 0
            for d in docs:
                s = (d.to_dict() or {}).get("status", "")
                if isinstance(s, str) and ("active" in s.lower() or s == "قيد التنفيذ"):
                    count += 1
            return count
        except Exception:
            return 0


def _build_chart_data() -> dict:
    """Build labels and sales totals for the last 6 months."""
    now = datetime.now(timezone.utc)
    base = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Compute (year, month) tuples for the last 6 months
    months = []
    y, m = base.year, base.month
    for i in range(5, -1, -1):
        mo = m - i
        yr = y
        while mo <= 0:
            mo += 12
            yr -= 1
        months.append((yr, mo))

    labels = [calendar.month_abbr[mo] for (_, mo) in months]
    totals = {(yr, mo): 0.0 for (yr, mo) in months}

    start_yr, start_mo = months[0]
    start_dt = datetime(start_yr, start_mo, 1, tzinfo=timezone.utc)
    last_yr, last_mo = months[-1]
    end_dt = (
        datetime(last_yr + 1, 1, 1, tzinfo=timezone.utc)
        if last_mo == 12
        else datetime(last_yr, last_mo + 1, 1, tzinfo=timezone.utc)
    )

    orders = order_repo.get_in_date_range(start_dt, end_dt)
    for order in orders:
        dt = order.get("date")
        if not isinstance(dt, datetime):
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        key = (dt.year, dt.month)
        if key not in totals:
            continue
        amt = parse_amount(order.get("total"))
        if amt is not None:
            totals[key] += amt

    return {
        "months": labels,
        "sales": [round(totals[(yr, mo)], 2) for (yr, mo) in months],
    }
