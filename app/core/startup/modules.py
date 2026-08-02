"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Startup

Initializes the enterprise module framework
during application startup.
"""

from flask import Flask

from app.core.modules import ModuleManager


def initialize_modules(app: Flask) -> ModuleManager:
    """
    Initialize the enterprise module framework.

    This function is responsible for creating the
    application's ModuleManager, registering all
    built-in modules, initializing them, and making
    the manager available throughout the application.

    Automatic module discovery will be introduced
    in Sprint 1.7.2.
    """

    manager = ModuleManager()

    # -------------------------------------------------
    # Register Built-in Modules
    # -------------------------------------------------
    #
    # Stage 1.7.1
    #
    # No enterprise modules are registered yet.
    #
    # The Dashboard, HR, Finance, Procurement,
    # Assets, Membership, Catering, and all future
    # modules will migrate into this framework
    # progressively.
    #
    # Example:
    #
    # manager.register_module(DashboardModule())
    #
    # -------------------------------------------------

    # -------------------------------------------------
    # Initialize Registered Modules
    # -------------------------------------------------

    manager.initialize_modules(app)

    # -------------------------------------------------
    # Store manager on the Flask application
    # -------------------------------------------------

    app.extensions["module_manager"] = manager

    return manager
