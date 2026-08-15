"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Default configuration registry implementation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

from app.core.configuration.exceptions import (
    ConfigurationContractException,
)
from app.core.configuration.module import (
    ModuleConfiguration,
)


class DefaultConfigurationRegistry:
    """
    Default concrete configuration registry.

    Stores module configuration definitions and
    produces independent resolved configuration
    instances when overrides are supplied.

    This class is an implementation of the
    ConfigurationRegistry contract.
    """

    def __init__(self) -> None:
        """
        Initialize an empty configuration registry.
        """

        self._configurations: Dict[
            str,
            ModuleConfiguration,
        ] = {}

    def register(
        self,
        configuration: ModuleConfiguration,
    ) -> ModuleConfiguration:
        """
        Register a module configuration definition.

        Raises:
            ConfigurationContractException:
                If the configuration is invalid or the
                module has already been registered.
        """

        if not isinstance(
            configuration,
            ModuleConfiguration,
        ):
            raise ConfigurationContractException(
                "Configuration registry requires "
                "a ModuleConfiguration instance."
            )

        if not configuration.module_code:
            raise ConfigurationContractException(
                "Configuration module code is required."
            )

        if configuration.module_code in (
            self._configurations
        ):
            raise ConfigurationContractException(
                "Configuration is already registered "
                f"for module '{configuration.module_code}'."
            )

        stored = deepcopy(
            configuration
        )

        self._configurations[
            configuration.module_code
        ] = stored

        return deepcopy(
            stored
        )

    def contains(
        self,
        module_code: str,
    ) -> bool:
        """
        Determine whether a module configuration
        is registered.
        """

        return module_code in (
            self._configurations
        )

    def get(
        self,
        module_code: str,
    ) -> ModuleConfiguration:
        """
        Return an independent copy of a registered
        module configuration.

        Raises:
            ConfigurationContractException:
                If no configuration is registered.
        """

        if not self.contains(
            module_code
        ):
            raise ConfigurationContractException(
                "No configuration is registered "
                f"for module '{module_code}'."
            )

        return deepcopy(
            self._configurations[
                module_code
            ]
        )

    def resolve(
        self,
        module_code: str,
        overrides: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ModuleConfiguration:
        """
        Resolve effective configuration for a module.

        Resolution begins with the registered
        configuration and applies supplied overrides
        to an independent configuration copy.

        The registered configuration is never mutated.
        """

        configuration = self.get(
            module_code
        )

        if overrides is not None:

            if not isinstance(
                overrides,
                dict,
            ):
                raise ConfigurationContractException(
                    "Configuration overrides must "
                    "be provided as a dictionary."
                )

            configuration.update(
                deepcopy(
                    overrides
                )
            )

        return configuration

    def unregister(
        self,
        module_code: str,
    ) -> ModuleConfiguration:
        """
        Remove and return a registered configuration.

        Raises:
            ConfigurationContractException:
                If no configuration is registered.
        """

        if not self.contains(
            module_code
        ):
            raise ConfigurationContractException(
                "No configuration is registered "
                f"for module '{module_code}'."
            )

        configuration = self._configurations.pop(
            module_code
        )

        return deepcopy(
            configuration
        )

    def clear(self) -> None:
        """
        Remove all registered configurations.
        """

        self._configurations.clear()

    def __len__(self) -> int:
        """
        Return the number of registered configurations.
        """

        return len(
            self._configurations
        )


__all__ = [
    "DefaultConfigurationRegistry",
]
