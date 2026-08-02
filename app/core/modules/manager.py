"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Module Manager

Controls module registration,
initialization, and lifecycle management.
"""


from typing import Iterable

from flask import Flask

from app.core.modules.base import BaseModule

from app.core.modules.registry import (
    ModuleRegistry,
)

from app.core.modules.exceptions import (
    InvalidModuleMetadataException,
    ModuleInitializationException,
)


class ModuleManager:
    """
    Enterprise module lifecycle manager.
    """

    def __init__(self):
        """
        Initialize module manager.
        """

        self.registry = ModuleRegistry()


    def register_module(
        self,
        module: BaseModule,
    ):
        """
        Validate and register a module.
        """

        try:

            module.metadata.validate()

        except Exception as error:

            raise InvalidModuleMetadataException(
                str(error)
            )

        self.registry.register(
            module
        )


    def register_modules(
        self,
        modules: Iterable[BaseModule],
    ):
        """
        Register multiple modules.
        """

        for module in modules:

            self.register_module(
                module
            )


    def initialize_modules(
        self,
        app: Flask,
    ):
        """
        Initialize all registered modules.
        """

        for module in (
            self.registry.all_modules()
        ):

            try:

                module.initialize(
                    app
                )

            except Exception as error:

                raise ModuleInitializationException(
                    f"Failed initializing "
                    f"{module.metadata.identifier}: "
                    f"{error}"
                )


    def get_module(
        self,
        module_code: str,
    ):
        """
        Retrieve a module.
        """

        return self.registry.get(
            module_code
        )


    def get_active_modules(
        self,
    ):
        """
        Return active modules.
        """

        return self.registry.active_modules()


    def module_count(
        self,
    ):
        """
        Return number of registered modules.
        """

        return self.registry.count()


    def clear(
        self,
    ):
        """
        Clear all modules.

        Mainly used during testing.
        """

        self.registry.clear()
