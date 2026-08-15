"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration definition registry implementation.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Iterable, Optional

from app.core.configuration.contracts import (
    ConfigurationRegistry,
)

from app.core.configuration.domain import (
    ConfigurationDefinition,
)

from app.core.configuration.exceptions import (
    ConfigurationContractException,
)


class DefaultConfigurationDefinitionRegistry(
    ConfigurationRegistry
):
    """
    Default concrete implementation of the
    ConfigurationRegistry contract.

    Stores configuration definitions independently
    from configuration values and providers.
    """

    def __init__(self) -> None:
        """
        Initialize an empty definition registry.
        """

        self._definitions: dict[
            str,
            ConfigurationDefinition,
        ] = {}

    def register(
        self,
        definition: ConfigurationDefinition,
    ) -> None:
        """
        Register a configuration definition.

        Raises:
            ConfigurationContractException:
                If the supplied object is not a
                ConfigurationDefinition or a definition
                with the same name already exists.
        """

        if not isinstance(
            definition,
            ConfigurationDefinition,
        ):
            raise ConfigurationContractException(
                "Configuration registry requires "
                "a ConfigurationDefinition instance."
            )

        if not definition.name:
            raise ConfigurationContractException(
                "Configuration definition name is required."
            )

        if definition.name in self._definitions:
            raise ConfigurationContractException(
                "Configuration definition is already "
                f"registered for '{definition.name}'."
            )

        self._definitions[
            definition.name
        ] = deepcopy(
            definition
        )

    def get_definition(
        self,
        name: str,
    ) -> Optional[ConfigurationDefinition]:
        """
        Retrieve an independent copy of a
        configuration definition.

        Returns:
            A configuration definition or None when
            no definition is registered.
        """

        definition = self._definitions.get(
            name
        )

        if definition is None:
            return None

        return deepcopy(
            definition
        )

    def definitions(
        self,
    ) -> Iterable[ConfigurationDefinition]:
        """
        Return independent copies of all registered
        configuration definitions.
        """

        return tuple(
            deepcopy(
                definition
            )
            for definition
            in self._definitions.values()
        )

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a definition is registered.
        """

        return name in self._definitions

    def clear(self) -> None:
        """
        Remove all registered definitions.
        """

        self._definitions.clear()

    def __len__(self) -> int:
        """
        Return the number of registered definitions.
        """

        return len(
            self._definitions
        )


__all__ = [
    "DefaultConfigurationDefinitionRegistry",
]
