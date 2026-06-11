"""
Routes package — registers all Flask Blueprints with the application.

Each module in this package defines a Blueprint for a single feature area.
The `register_all` function is called once in the application factory.
"""

from flask import Flask


def register_all(app: Flask) -> None:
    """Import and register every blueprint with the Flask app."""
    from backend.routes.auth_routes import auth_bp
    from backend.routes.dashboard_routes import dashboard_bp
    from backend.routes.medicine_routes import medicines_bp
    from backend.routes.order_routes import orders_bp
    from backend.routes.supplier_routes import suppliers_bp
    from backend.routes.inventory_routes import inventory_bp
    from backend.routes.report_routes import reports_bp
    from backend.routes.misc_routes import misc_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(misc_bp)
