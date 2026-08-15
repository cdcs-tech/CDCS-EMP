"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Startup

Coordinates discovery, validation,
loading, registration and initialization
of enterprise modules.
"""


import logging

from flask import Flask

from app.core.validation import (
    BaseValidator,
)

from app.core.workflow import (
    workflow_registry,
)

from app.core.discovery import (
    ModuleDependencyValidator,
    ModuleDiscovery,
    ModuleLoader,
)

from app.core.modules import ModuleManager

from app.core.services import (
    service_registry,
    service_container,
)

from app.core.configuration.composition import (
    register_configuration_service,
)


logger = logging.getLogger(__name__)


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
        Service Registration
    """


    manager = ModuleManager()


    discovery = ModuleDiscovery()

    manifests = discovery.discover()


    logger.info(
        "Discovered %s module manifest(s).",
        len(manifests),
    )



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



    loader = ModuleLoader(manager)


    loaded_modules = loader.load(
        ordered_manifests
    )


    logger.info(
        "Loaded %s module(s).",
        len(loaded_modules),
    )



    for module in loaded_modules:

        logger.info(
            "Initializing module: %s",
            module.metadata.code,
        )

        module.initialize(app)

    # --------------------------------------------------
    # Configuration Service
    # --------------------------------------------------

    register_configuration_service(
        app
    )


    logger.info(
        "Registered %s enterprise service(s).",
        service_registry.count(),
    )


    logger.info(
        "Available service instances: %s.",
        service_container.count(),
    )



    logger.info(
        "Enterprise Module Framework initialized."
    )


    # --------------------------------------------------
    # Expose Enterprise Framework Services
    # --------------------------------------------------

    app.extensions[
        "module_manager"
    ] = manager


    app.extensions[
        "workflow_registry"
    ] = workflow_registry


    return manager
