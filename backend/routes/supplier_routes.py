"""
Supplier routes.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from backend.auth.decorators import login_required
from backend.services.supplier_service import get_suppliers_with_stats, add_supplier, get_supplier_by_id, update_supplier, delete_supplier

logger = logging.getLogger(__name__)

suppliers_bp = Blueprint("suppliers", __name__)


@suppliers_bp.route("/suppliers")
@login_required
def suppliers():
    """List all suppliers with summary statistics."""
    try:
        suppliers_list, stats = get_suppliers_with_stats()
    except Exception as exc:
        logger.error("[suppliers] Failed to load suppliers: %s", exc)
        suppliers_list, stats = [], {}
        flash("An error occurred while loading suppliers", "error")
    return render_template(
        "suppliers/list.html", active="suppliers", suppliers=suppliers_list, stats=stats
    )


@suppliers_bp.route("/suppliers/add", methods=["GET"])
@login_required
def add_supplier_form():
    """Display the add-supplier form."""
    return render_template("suppliers/add.html", active="suppliers")


@suppliers_bp.route("/suppliers/add", methods=["POST"])
@login_required
def add_supplier_submit():
    """Process the add-supplier form submission."""
    success = add_supplier(request.form)
    if success:
        flash("Supplier added successfully!", "success")
        return redirect(url_for("suppliers.suppliers"))
    flash("An error occurred while adding the supplier", "error")
    return redirect(url_for("suppliers.add_supplier_form"))


@suppliers_bp.route("/suppliers/edit/<doc_id>", methods=["GET"])
@login_required
def edit_supplier_form(doc_id):
    """Display the edit-supplier form."""
    supplier = get_supplier_by_id(doc_id)
    if not supplier:
        flash("Supplier not found", "error")
        return redirect(url_for("suppliers.suppliers"))
    return render_template("suppliers/edit.html", active="suppliers", supplier=supplier)


@suppliers_bp.route("/suppliers/edit/<doc_id>", methods=["POST"])
@login_required
def edit_supplier_submit(doc_id):
    """Process the edit-supplier form submission."""
    success = update_supplier(doc_id, request.form)
    if success:
        flash("Supplier updated successfully", "success")
    else:
        flash("An error occurred while updating supplier", "error")
    return redirect(url_for("suppliers.suppliers"))


@suppliers_bp.route("/suppliers/delete/<doc_id>", methods=["POST"])
@login_required
def delete_supplier_submit(doc_id):
    """Process the delete-supplier request."""
    success = delete_supplier(doc_id)
    if success:
        flash("Supplier deleted successfully", "success")
    else:
        flash("An error occurred while deleting supplier", "error")
    return redirect(url_for("suppliers.suppliers"))
