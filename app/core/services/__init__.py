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
    ServiceRegistry,
    ServiceDefinition,
    service_registry,
)


# ---------------------------------------------------------
# Dependency Injection Container
# ---------------------------------------------------------

from app.core.services.container import (
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

    "ServiceRegistry",

    "ServiceDefinition",

    "service_registry",


    # Dependency Container

    "ServiceContainer",

    "service_container",

]
