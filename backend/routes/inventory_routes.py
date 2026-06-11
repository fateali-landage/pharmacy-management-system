"""
Inventory routes.
"""

import logging
from flask import Blueprint, render_template, flash
from backend.auth.decorators import login_required
from backend.services.inventory_service import get_inventory_with_stats

logger = logging.getLogger(__name__)

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory")
@login_required
def inventory():
    """List all inventory items with aggregate statistics."""
    try:
        items, inv_stats = get_inventory_with_stats()
    except Exception as exc:
        logger.error("[inventory] Failed to load inventory: %s", exc)
        items, inv_stats = [], {}
        flash("An error occurred while fetching inventory", "error")
    return render_template(
        "inventory/list.html", active="inventory", items=items, inv_stats=inv_stats
    )
