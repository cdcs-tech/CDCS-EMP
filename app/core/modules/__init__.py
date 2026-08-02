"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Framework

Public exports for the module framework.
"""


from app.core.modules.base import (
    BaseModule,
)

from app.core.modules.metadata import (
    ModuleMetadata,
)

from app.core.modules.registry import (
    ModuleRegistry,
)

from app.core.modules.manager import (
    ModuleManager,
)

from app.core.modules.exceptions import (
    ModuleFrameworkException,
    ModuleRegistrationException,
    ModuleAlreadyRegisteredException,
    ModuleNotFoundException,
    InvalidModuleMetadataException,
    ModuleDependencyException,
    ModuleInitializationException,
)


__all__ = [

    "BaseModule",

    "ModuleMetadata",

    "ModuleRegistry",

    "ModuleManager",

    "ModuleFrameworkException",

    "ModuleRegistrationException",

    "ModuleAlreadyRegisteredException",

    "ModuleNotFoundException",

    "InvalidModuleMetadataException",

    "ModuleDependencyException",

    "ModuleInitializationException",

]
