"""
Miscellaneous routes — root redirect and contact page.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for
from backend.auth.decorators import login_required

logger = logging.getLogger(__name__)

misc_bp = Blueprint("misc", __name__)


@misc_bp.route("/")
def index():
    """Redirect the root URL to the login page."""
    return redirect(url_for("auth.login"))


@misc_bp.route("/contact")
@login_required
def contact():
    """Render the contact / about page."""
    return render_template("misc/contact.html", active="contact")
