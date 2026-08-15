"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

In-memory configuration provider.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Optional

from app.core.configuration.contracts import (
    ConfigurationProvider,
)

from app.core.configuration.domain import (
    ConfigurationKey,
    ConfigurationValue,
)


class MemoryConfigurationProvider(
    ConfigurationProvider
):
    """
    In-memory implementation of the
    ConfigurationProvider contract.

    This provider is intended as a lightweight
    reference implementation and test provider.

    Values are isolated from callers through
    defensive copying.
    """

    def __init__(self) -> None:
        """
        Initialize an empty configuration store.
        """

        self._values: dict[
            ConfigurationKey,
            ConfigurationValue,
        ] = {}

    def get(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:
        """
        Retrieve a configuration value.

        Returns:
            An independent copy of the stored value,
            or None when the key is not registered.
        """

        value = self._values.get(
            key
        )

        if value is None:
            return None

        return deepcopy(
            value
        )

    def set(
        self,
        key: ConfigurationKey,
        value: Any,
    ) -> ConfigurationValue:
        """
        Store or replace a configuration value.

        Returns:
            The stored configuration value as an
            independent copy.
        """

        configuration_value = (
            ConfigurationValue(
                key=key,
                value=deepcopy(
                    value
                ),
                source="memory",
            )
        )

        self._values[
            key
        ] = configuration_value

        return deepcopy(
            configuration_value
        )

    def delete(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Delete a configuration value.

        Returns:
            True when a value was removed,
            otherwise False.
        """

        if key not in self._values:
            return False

        del self._values[
            key
        ]

        return True

    def exists(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Determine whether a configuration value
        exists for the supplied key.
        """

        return key in self._values

    def clear(self) -> None:
        """
        Remove all stored configuration values.
        """

        self._values.clear()

    def __len__(self) -> int:
        """
        Return the number of stored values.
        """

        return len(
            self._values
        )


__all__ = [
    "MemoryConfigurationProvider",
]
