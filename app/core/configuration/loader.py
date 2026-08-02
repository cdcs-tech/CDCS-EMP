"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Loader

Creates and prepares module configuration
objects before module initialization.
"""


from typing import Dict, Optional

from app.core.configuration.module import (
    ModuleConfiguration,
)


class ModuleConfigurationLoader:
    """
    Loads module configuration definitions.
    """


    def __init__(
        self,
    ):
        """
        Initialize configuration loader.
        """

        self.defaults: Dict[
            str,
            Dict
        ] = {}


    def register_defaults(
        self,
        module_code: str,
        settings: Dict,
    ):
        """
        Register default configuration
        for a module.

        Args:

            module_code:
                Module identifier.

            settings:
                Default settings.
        """

        self.defaults[module_code] = settings


    def load(
        self,
        module_code: str,
        overrides: Optional[
            Dict
        ] = None,
    ) -> ModuleConfiguration:
        """
        Create module configuration.

        Args:

            module_code:
                Module identifier.

            overrides:
                Runtime configuration overrides.

        Returns:

            ModuleConfiguration instance.
        """

        settings = {}

        default_settings = self.defaults.get(
            module_code,
            {},
        )

        settings.update(
            default_settings
        )


        if overrides:

            settings.update(
                overrides
            )


        return ModuleConfiguration(
            module_code=module_code,
            settings=settings,
        )
