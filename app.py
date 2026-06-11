"""
Pharmacy Management System — Application Entry Point.

This file is intentionally minimal. All application setup logic has been
moved into the `backend` package (`backend/__init__.py`).

Run locally:
    python app.py

Production (Gunicorn):
    gunicorn "app:app"
"""

from backend import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
