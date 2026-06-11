"""
Report routes.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from backend.auth.decorators import login_required
from backend.services.report_service import get_recent_reports, create_report, get_medicines_for_report

logger = logging.getLogger(__name__)

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
@login_required
def reports():
    """List the most recent pharmacy reports."""
    try:
        reports_list = get_recent_reports()
    except Exception as exc:
        logger.error("[reports] Failed to load reports: %s", exc)
        reports_list = []
        flash("An error occurred while loading reports", "error")
    return render_template("reports/list.html", active="reports", reports=reports_list)


@reports_bp.route("/reports/create", methods=["GET", "POST"])
@login_required
def reports_create():
    """Create a new pharmacy report (GET: form, POST: persist)."""
    if request.method == "POST":
        try:
            user_id = session.get("user", {}).get("uid") or session.get("user", {}).get("email")
            success = create_report(request.form, user_id)
            if success:
                flash(g._("report_created_success"), "success")
            else:
                flash(g._("error_creating_report"), "error")
        except Exception as exc:
            logger.error("[reports] Error creating report: %s", exc)
            flash(g._("error_creating_report"), "error")
        return redirect(url_for("reports.reports"))

    # GET — show the form
    try:
        medicines = get_medicines_for_report()
    except Exception as exc:
        logger.error("[reports] Failed to load medicines for report form: %s", exc)
        medicines = []
    return render_template("reports/create.html", active="reports", medicines=medicines)
