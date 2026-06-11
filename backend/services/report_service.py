"""
Report service — business logic for creating and fetching reports.
"""

import logging
from firebase_admin import firestore

from database.repositories.report_repository import report_repo
from database.repositories.medicine_repository import medicine_repo

logger = logging.getLogger(__name__)


def get_recent_reports(limit: int = 10) -> list:
    """Return the most recent report documents."""
    return report_repo.get_recent(limit=limit)


def create_report(form, session_user_id: str) -> bool:
    """
    Build and persist a new report document from form data.

    Args:
        form:            Flask request.form
        session_user_id: The current user's UID or email.

    Returns:
        True on success, False on failure.
    """
    title = form.get("title", "Untitled Report").strip()
    report_type = form.get("report_type", "custom")
    selected_medicine_ids = form.getlist("selected_medicines")
    report_content = form.get("report_content", "")
    include_stock = "include_stock" in form
    include_pricing = "include_pricing" in form
    export_format = form.get("export_format", "pdf")

    # Fetch selected medicine details
    medicines_data = []
    for med_id in selected_medicine_ids:
        med = medicine_repo.get_by_id(med_id)
        if med:
            medicines_data.append({
                "id": med_id,
                "name": med.get("name", "Unnamed Medicine"),
                "stock": med.get("stock", 0),
                "price": med.get("price", 0),
                "category": med.get("category", "Uncategorized"),
            })

    report_data = {
        "title": title,
        "type": report_type,
        "content": report_content,
        "medicines": medicines_data,
        "include_stock": include_stock,
        "include_pricing": include_pricing,
        "export_format": export_format,
        "status": "draft",
        "created_at": firestore.SERVER_TIMESTAMP,
        "created_by": session_user_id,
        "updated_at": firestore.SERVER_TIMESTAMP,
    }

    doc_id = report_repo.add(report_data)
    if doc_id:
        logger.info("[report_service] Created report '%s' id=%s", title, doc_id)
        return True
    logger.error("[report_service] Failed to create report '%s'", title)
    return False


def get_medicines_for_report() -> list:
    """Return medicines with stock > 0 for the report creation form."""
    return medicine_repo.get_with_stock()
