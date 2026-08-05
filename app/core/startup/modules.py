"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Startup

Coordinates discovery, validation,
loading, registration and initialization
of enterprise modules.
"""

import logging

from flask import Flask

from app.core.discovery import (
    ModuleDependencyValidator,
    ModuleDiscovery,
    ModuleLoader,
)

from app.core.modules import ModuleManager

from app.core.crud.registry import (
    CRUDDefinition,
    crud_registry,
)


logger = logging.getLogger(__name__)


def register_module_crud(module):
    """
    Register CRUD capabilities exposed
    by an enterprise module.
    """

    crud_config = (
        module.get_crud_config()
    )

    if crud_config is None:
        return


    definition = CRUDDefinition(

        module_name=(
            crud_config.module_name
        ),

        entity_name=(
            crud_config.entity_name
        ),
    )


    crud_registry.register(
        definition
    )


    logger.info(
        "Registered CRUD definition: %s.%s",
        crud_config.module_name,
        crud_config.entity_name,
    )


def initialize_modules(app: Flask) -> ModuleManager:
    """
    Initialize the Enterprise Module Framework.

    Startup pipeline:

        ModuleManager
            ↓
        Discovery
            ↓
        Validation
            ↓
        Loading
            ↓
        Initialization
            ↓
        CRUD Registration
    """


    # --------------------------------------------------
    # Create Module Manager
    # --------------------------------------------------

    manager = ModuleManager()


    # --------------------------------------------------
    # Discover Available Modules
    # --------------------------------------------------

    discovery = ModuleDiscovery()

    manifests = discovery.discover()


    logger.info(
        "Discovered %s module manifest(s).",
        len(manifests),
    )


    # --------------------------------------------------
    # Validate Dependencies
    # --------------------------------------------------

    validator = ModuleDependencyValidator(
        manifests
    )

    validator.validate()


    ordered_manifests = (
        validator.dependency_order()
    )


    logger.info(
        "Validated module dependencies."
    )


    # --------------------------------------------------
    # Load Modules
    # --------------------------------------------------

    loader = ModuleLoader(manager)

    loaded_modules = loader.load(
        ordered_manifests
    )


    logger.info(
        "Loaded %s module(s).",
        len(loaded_modules),
    )


    # --------------------------------------------------
    # Initialize Modules
    # --------------------------------------------------

    for module in loaded_modules:

        logger.info(
            "Initializing module: %s",
            module.metadata.code,
        )


        module.initialize(app)


        register_module_crud(
            module
        )


    logger.info(
        "Enterprise Module Framework initialized."
    )


    # --------------------------------------------------
    # Expose Module Manager
    # --------------------------------------------------

    app.extensions[
        "module_manager"
    ] = manager


    # --------------------------------------------------
    # Expose CRUD Registry
    # --------------------------------------------------

    app.extensions[
        "crud_registry"
    ] = crud_registry


    return manager
