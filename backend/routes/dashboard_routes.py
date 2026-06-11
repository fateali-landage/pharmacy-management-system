"""
Dashboard routes.
"""

import logging
from flask import Blueprint, render_template, flash
from backend.auth.decorators import login_required
from backend.services.dashboard_service import get_dashboard_data

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """Render the main dashboard with live stats and chart data."""
    try:
        data = get_dashboard_data()
    except Exception as exc:
        logger.error("[dashboard] Failed to load dashboard data: %s", exc)
        data = {"stats": {}, "chart_data": {"months": [], "sales": []}}
        flash("Could not load dashboard data", "error")

    return render_template(
        "dashboard/index.html",
        active="dashboard",
        stats=data["stats"],
        chart_data=data["chart_data"],
    )
