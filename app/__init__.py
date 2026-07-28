"""
CDCS Enterprise Management Platform (CDCS-EMP)

Application Factory
"""

import os

from flask import Flask

from app.config import config
from app.extensions import (
    bcrypt,
    csrf,
    db,
    login_manager,
    migrate,
)
from app.logging import configure_logging
# Import models so Flask-Migrate can discover them
from app import models  # noqa: F401


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name (str, optional):
            Configuration profile to load.
            If None, the value is read from the FLASK_ENV
            environment variable.

    Returns:
        Flask:
            Configured Flask application instance.
    """

    # ---------------------------------------------------------
    # Create Flask Application
    # ---------------------------------------------------------
    app = Flask(__name__)

    # ---------------------------------------------------------
    # Load Configuration
    # ---------------------------------------------------------
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app.config.from_object(config[config_name])

    # ---------------------------------------------------------
    # Initialize Flask Extensions
    # ---------------------------------------------------------
    initialize_extensions(app)

    # ---------------------------------------------------------
    # Register Blueprints
    # ---------------------------------------------------------
    register_blueprints(app)

    # ---------------------------------------------------------
    # Register Error Handlers
    # ---------------------------------------------------------
    register_error_handlers(app)

    # ---------------------------------------------------------
    # Configure Logging
    # ---------------------------------------------------------
    configure_logging(app)

    app.logger.info(
        "CDCS-EMP %s started in %s mode.",
        app.config.get("APP_VERSION"),
        config_name,
    )

    return app


def initialize_extensions(app):
    """
    Initialize all Flask extensions.
    """

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)


def register_blueprints(app):
    """
    Register application blueprints.
    """

    from app.blueprints.core import core_bp

    app.register_blueprint(core_bp)

    # Future blueprint registrations
    #
    # from app.blueprints.auth import auth_bp
    # from app.blueprints.dashboard import dashboard_bp
    # from app.blueprints.admin import admin_bp
    # from app.blueprints.api import api_bp
    #
    # app.register_blueprint(auth_bp, url_prefix="/auth")
    # app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    # app.register_blueprint(admin_bp, url_prefix="/admin")
    # app.register_blueprint(api_bp, url_prefix="/api")


def register_error_handlers(app):
    """
    Register global application error handlers.
    """

    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning("404 Not Found: %s", error)

        return {
            "status": 404,
            "error": "Not Found",
            "message": "The requested resource could not be found.",
        }, 404

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.exception("Internal Server Error")

        return {
            "status": 500,
            "error": "Internal Server Error",
            "message": "An unexpected error has occurred.",
        }, 500
