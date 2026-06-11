"""
Medicine service — business logic for the medicines module.

Routes call this service; this service calls the repository.
No Firestore imports belong in routes.
"""

import logging
from database.repositories.medicine_repository import medicine_repo
from backend.models.medicine import medicine_from_form

logger = logging.getLogger(__name__)


def get_all_medicines() -> list:
    """Return all medicine documents as a list of dicts."""
    return medicine_repo.get_all()


def get_medicines_with_stock() -> list:
    """Return medicines that have stock > 0, ordered by name."""
    return medicine_repo.get_with_stock()


def add_medicine(form) -> bool:
    """
    Persist a new medicine from form data.

    Args:
        form: Flask request.form

    Returns:
        True on success, False on failure.
    """
    data = medicine_from_form(form)
    doc_id = medicine_repo.add(data)
    if doc_id:
        logger.info("[medicine_service] Added medicine '%s' (id=%s)", data.get("name"), doc_id)
        return True
    logger.error("[medicine_service] Failed to add medicine '%s'", data.get("name"))
    return False


def get_medicine_by_id(doc_id: str) -> dict | None:
    """Retrieve a single medicine by its doc_id."""
    return medicine_repo.get_by_id(doc_id)


def update_medicine(doc_id: str, form) -> bool:
    """Update an existing medicine document using form data."""
    data = medicine_from_form(form)
    success = medicine_repo.update(doc_id, data)
    if success:
        logger.info("[medicine_service] Updated medicine '%s' (id=%s)", data.get("name"), doc_id)
        return True
    logger.error("[medicine_service] Failed to update medicine '%s' (id=%s)", data.get("name"), doc_id)
    return False


def delete_medicine(doc_id: str) -> bool:
    """Delete a medicine document by its doc_id."""
    success = medicine_repo.delete(doc_id)
    if success:
        logger.info("[medicine_service] Deleted medicine id=%s", doc_id)
        return True
    logger.error("[medicine_service] Failed to delete medicine id=%s", doc_id)
    return False
