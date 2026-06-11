"""
Medicine routes.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from backend.auth.decorators import login_required
from backend.services.medicine_service import get_all_medicines, add_medicine, get_medicine_by_id, update_medicine, delete_medicine

logger = logging.getLogger(__name__)

medicines_bp = Blueprint("medicines", __name__)


@medicines_bp.route("/medicines")
@login_required
def medicines():
    """List all medicines."""
    try:
        meds = get_all_medicines()
    except Exception as exc:
        logger.error("[medicines] Failed to load medicines: %s", exc)
        meds = []
        flash("An error occurred while loading medicines", "error")
    return render_template("medicines/list.html", active="medicines", meds=meds)


@medicines_bp.route("/medicines/add", methods=["GET"])
@login_required
def add_medicine_form():
    """Show the add-medicine form."""
    return render_template("medicines/add.html", active="medicines")


@medicines_bp.route("/medicines/add", methods=["POST"])
@login_required
def add_medicine_submit():
    """Process the add-medicine form submission."""
    success = add_medicine(request.form)
    if success:
        flash("Medicine added successfully", "success")
    else:
        flash("An error occurred while adding medicine", "error")
    return redirect(url_for("medicines.medicines"))


@medicines_bp.route("/medicines/edit/<doc_id>", methods=["GET"])
@login_required
def edit_medicine_form(doc_id):
    """Show the edit-medicine form."""
    med = get_medicine_by_id(doc_id)
    if not med:
        flash("Medicine not found", "error")
        return redirect(url_for("medicines.medicines"))
    return render_template("medicines/edit.html", active="medicines", med=med)


@medicines_bp.route("/medicines/edit/<doc_id>", methods=["POST"])
@login_required
def edit_medicine_submit(doc_id):
    """Process the edit-medicine form submission."""
    success = update_medicine(doc_id, request.form)
    if success:
        flash("Medicine updated successfully", "success")
    else:
        flash("An error occurred while updating medicine", "error")
    return redirect(url_for("medicines.medicines"))


@medicines_bp.route("/medicines/delete/<doc_id>", methods=["POST"])
@login_required
def delete_medicine_submit(doc_id):
    """Process the delete-medicine request."""
    success = delete_medicine(doc_id)
    if success:
        flash("Medicine deleted successfully", "success")
    else:
        flash("An error occurred while deleting medicine", "error")
    return redirect(url_for("medicines.medicines"))
