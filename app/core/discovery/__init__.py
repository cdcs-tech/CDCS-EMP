"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Discovery Framework

Public interface for module discovery services.
"""

from app.core.discovery.discovery import (
    ModuleDiscovery,
)

from app.core.discovery.loader import (
    ModuleLoader,
)

from app.core.discovery.manifest import (
    ModuleManifest,
)

from app.core.discovery.validator import (
    ModuleDependencyValidator,
)

__all__ = [

    "ModuleManifest",

    "ModuleDiscovery",

    "ModuleDependencyValidator",

    "ModuleLoader",

]
