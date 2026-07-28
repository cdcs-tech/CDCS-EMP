"""
CDCS Enterprise Management Platform (CDCS-EMP)

Application Factory
"""

import logging
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

# Import models so Flask-Migrate can discover them
from app import models  # noqa: F401


def create_app(config_name=None):
    """
    Application Factory
    """

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # -------------------------------------------------------
    # Register Blueprints
    # -------------------------------------------------------

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.blueprints.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # -------------------------------------------------------
    # Logging Configuration
    # -------------------------------------------------------

    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    return app
