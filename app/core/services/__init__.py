"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Public service layer interface.
"""


# ---------------------------------------------------------
# Base Service
# ---------------------------------------------------------

from app.core.services.base import (
    BaseService,
)


# ---------------------------------------------------------
# Service Exceptions
# ---------------------------------------------------------

from app.core.services.exceptions import (
    ServiceException,
    ServiceValidationException,
    ServiceNotFoundException,
    ServiceConflictException,
    ServiceOperationException,
)


# ---------------------------------------------------------
# Service Registry
# ---------------------------------------------------------

from app.core.services.registry import (
    ServiceRegistryException,
    ServiceDefinitionException,
    ServiceRegistrationException,
    ServiceResolutionException,
    ServiceRegistry,
    ServiceDefinition,
    service_registry,
)


# ---------------------------------------------------------
# Dependency Injection Container
# ---------------------------------------------------------

from app.core.services.container import (
    ServiceContainerException,
    ServiceAlreadyRegisteredException,
    ServiceNotRegisteredException,
    ServiceContainer,
    service_container,
)


__all__ = [

    # Base Service

    "BaseService",


    # Exceptions

    "ServiceException",

    "ServiceValidationException",

    "ServiceNotFoundException",

    "ServiceConflictException",

    "ServiceOperationException",


    # Registry

    "ServiceRegistryException",
    "ServiceDefinitionException",
    "ServiceRegistrationException",
    "ServiceResolutionException",
    "ServiceRegistry",
    "ServiceDefinition",
    "service_registry",


    # Dependency Container

    "ServiceContainerException",

    "ServiceAlreadyRegisteredException",

    "ServiceNotRegisteredException",

    "ServiceContainer",

    "service_container",

]
