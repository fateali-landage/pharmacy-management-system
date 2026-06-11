"""
Order routes.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from backend.auth.decorators import login_required
from backend.services.order_service import get_orders_with_stats, create_order, delete_order
from database.repositories.inventory_repository import inventory_repo
from database.repositories.supplier_repository import supplier_repo

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/orders")
@login_required
def orders():
    """List orders with summary statistics."""
    try:
        orders_list, stats = get_orders_with_stats()
    except Exception as exc:
        logger.error("[orders] Failed to load orders: %s", exc)
        orders_list, stats = [], {}
        flash("An error occurred while loading orders", "error")
    return render_template("orders/list.html", active="orders", orders=orders_list, stats=stats)


@orders_bp.route("/orders/create", methods=["GET"])
@login_required
def create_order_form():
    """Show the create-order form with inventory items and supplier list."""
    try:
        items = inventory_repo.get_all()
        suppliers = supplier_repo.get_all()
    except Exception as exc:
        logger.error("[orders] Failed to load create-order form data: %s", exc)
        items, suppliers = [], []
        flash("An error occurred while preparing the create order page", "error")
    return render_template(
        "orders/create.html", active="inventory", items=items, suppliers=suppliers
    )


@orders_bp.route("/orders/create", methods=["POST"])
@login_required
def create_order_submit():
    """Process the create-order form submission."""
    user = session.get("user", {})
    success = create_order(request.form, user)
    if success:
        flash("Order created successfully", "success")
    else:
        flash("An error occurred while creating the order", "error")
    return redirect(url_for("orders.orders"))


@orders_bp.route("/orders/delete/<doc_id>", methods=["POST"])
@login_required
def delete_order_submit(doc_id):
    """Process the delete-order request."""
    success = delete_order(doc_id)
    if success:
        flash("Order deleted successfully", "success")
    else:
        flash("An error occurred while deleting order", "error")
    return redirect(url_for("orders.orders"))
