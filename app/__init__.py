"""
CDCS Enterprise Management Platform (CDCS-EMP)

Application Factory
"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template

from app import models  # noqa: F401
from app.branding.brand import BRAND
from app.config import config
from app.core.platform.lifecycle import (
    ApplicationLifecycle,
)
from app.extensions import (
    bcrypt,
    csrf,
    db,
    login_manager,
    migrate,
)

# ---------------------------------------------------------
# Environment Configuration
# ---------------------------------------------------------

environment = os.getenv(
    "FLASK_ENV",
    "development",
)

dotenv_file = f".env.{environment}"

if os.path.exists(dotenv_file):
    load_dotenv(dotenv_file)


def create_app(config_name=None):
    """
    CDCS-EMP Application Factory.
    """

    if config_name is None:
        config_name = os.getenv(
            "FLASK_ENV",
            "development",
        )

    app = Flask(__name__)

    # -----------------------------------------------------
    # Load Configuration
    # -----------------------------------------------------

    app.config.from_object(
        config[config_name]
    )

    # -----------------------------------------------------
    # Initialize Flask Extensions
    # -----------------------------------------------------

    db.init_app(app)

    migrate.init_app(
        app,
        db,
    )

    bcrypt.init_app(app)

    login_manager.init_app(app)

    csrf.init_app(app)

    # -----------------------------------------------------
    # Register Core Blueprints
    #
    # NOTE:
    # These remain here until each component is migrated
    # into the Enterprise Module Framework.
    # -----------------------------------------------------

    from app.auth import auth_bp

    app.register_blueprint(
        auth_bp
    )

    from app.blueprints.dashboard import (
        dashboard_bp,
    )

    app.register_blueprint(
        dashboard_bp
    )

    # -----------------------------------------------------
    # Initialize Application Lifecycle
    # -----------------------------------------------------

    lifecycle = ApplicationLifecycle()

    lifecycle.start(
        app
    )

    # -----------------------------------------------------
    # Logging Configuration
    # -----------------------------------------------------

    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
        )

    # -----------------------------------------------------
    # Error Handlers
    # -----------------------------------------------------

    @app.errorhandler(401)
    def unauthorized(error):
        return (
            render_template(
                "auth/unauthorized.html"
            ),
            401,
        )

    @app.errorhandler(403)
    def forbidden(error):
        return (
            render_template(
                "auth/forbidden.html"
            ),
            403,
        )

    # -----------------------------------------------------
    # Context Processors
    # -----------------------------------------------------

    from app.navigation.menu import (
        MENU_ITEMS,
    )
    from app.security.authorization import (
        AuthorizationService,
    )

    @app.context_processor
    def inject_navigation():
        visible_items = []

        for item in MENU_ITEMS:
            visible_item = {
                key: value
                for key, value in item.items()
                if key not in {
                    "children",
                    "hide_if_empty",
                }
            }

            if item.get("children") is not None:
                visible_children = []

                for child in item["children"]:
                    permission = child.get("permission")

                    if (
                        permission
                        and not AuthorizationService.has_permission(
                            permission
                        )
                    ):
                        continue

                    visible_children.append({
                        key: value
                        for key, value in child.items()
                        if key != "permission"
                    })

                if (
                    item.get("hide_if_empty")
                    and not visible_children
                ):
                    continue

                visible_item["children"] = visible_children

            visible_items.append(visible_item)

        return {
            "menu_items": visible_items,
        }

    @app.context_processor
    def inject_brand():
        return {
            "brand": BRAND,
        }

    return app
