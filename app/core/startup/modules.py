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

from app.core.execution import (
    CommandDispatcher,
)

from app.core.execution.policy import (
    PermissionAwareExecutionAuthorizer,
)

from app.core.execution.security import (
    RegistryBackedPermissionExecutionPolicy,
)

from app.core.security.authorization import (
    authorization_engine,
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
        Execution Permission Composition
            ↓
        Service Registration
    """

    manager = ModuleManager()

    # --------------------------------------------------
    # Application Execution Infrastructure
    # --------------------------------------------------

    command_dispatcher = CommandDispatcher()

    app.extensions[
        "command_dispatcher"
    ] = command_dispatcher

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
    # Execution Authorization Composition
    # --------------------------------------------------

    execution_permission_policy = (
        RegistryBackedPermissionExecutionPolicy()
    )

    for module in loaded_modules:

        permission_mappings = (
            module.get_execution_permissions()
        )

        for command_name, permission_code in (
            permission_mappings.items()
        ):
            execution_permission_policy.register(
                command_name,
                permission_code,
            )

    execution_permission_policy.validate_registered_permissions()

    def evaluate_execution_permission(
        command,
        context,
        permission,
    ):
        """
        Evaluate an execution permission through
        the established application authorization engine.
        """

        return authorization_engine.can(
            context.user_id,
            permission.code,
            context=context,
        )

    execution_authorizer = (
        PermissionAwareExecutionAuthorizer(
            execution_permission_policy,
            evaluate_execution_permission,
        )
    )

    command_dispatcher.set_authorizer(
        execution_authorizer
    )

    app.extensions[
        "execution_permission_policy"
    ] = execution_permission_policy

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
