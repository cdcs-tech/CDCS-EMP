"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Registry

Central registry for managing installed
application modules.
"""


from typing import Dict, List, Optional

from app.core.modules.base import BaseModule

from app.core.modules.exceptions import (
    ModuleAlreadyRegisteredException,
    ModuleNotFoundException,
)


class ModuleRegistry:
    """
    Central registry of enterprise modules.
    """

    def __init__(self):
        """
        Initialize empty module registry.
        """

        self._modules: Dict[str, BaseModule] = {}


    def register(
        self,
        module: BaseModule,
    ):
        """
        Register a module.

        Raises:
            ModuleAlreadyRegisteredException
        """

        identifier = (
            module.metadata.identifier
        )

        if identifier in self._modules:
            raise ModuleAlreadyRegisteredException(
                f"Module '{identifier}' "
                "is already registered."
            )

        self._modules[identifier] = module


    def unregister(
        self,
        module_code: str,
    ):
        """
        Remove a module from registry.
        """

        identifier = module_code.upper()

        if identifier not in self._modules:
            raise ModuleNotFoundException(
                f"Module '{identifier}' "
                "was not found."
            )

        del self._modules[identifier]


    def get(
        self,
        module_code: str,
    ) -> BaseModule:
        """
        Retrieve a module by code.
        """

        identifier = module_code.upper()

        module = self._modules.get(
            identifier
        )

        if module is None:
            raise ModuleNotFoundException(
                f"Module '{identifier}' "
                "was not found."
            )

        return module


    def exists(
        self,
        module_code: str,
    ) -> bool:
        """
        Check whether module exists.
        """

        return (
            module_code.upper()
            in self._modules
        )


    def all_modules(
        self,
    ) -> List[BaseModule]:
        """
        Return all registered modules.
        """

        return list(
            self._modules.values()
        )


    def active_modules(
        self,
    ) -> List[BaseModule]:
        """
        Return only active modules.
        """

        return [
            module
            for module in self._modules.values()
            if module.is_active()
        ]


    def count(
        self,
    ) -> int:
        """
        Return number of registered modules.
        """

        return len(
            self._modules
        )


    def clear(
        self,
    ):
        """
        Clear registry.

        Mainly useful for testing.
        """

        self._modules.clear()


    def to_dict(
        self,
    ):
        """
        Export module registry information.
        """

        return [
            module.metadata.to_dict()
            for module in self._modules.values()
        ]
