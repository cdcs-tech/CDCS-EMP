"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration service contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional

from app.core.configuration.domain import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationValue,
)


class ConfigurationProvider(ABC):
    """
    Contract for configuration providers.

    Providers are responsible for retrieving
    configuration values from a particular source.
    """

    @abstractmethod
    def get(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:
        """
        Retrieve a configuration value.
        """

        raise NotImplementedError

    @abstractmethod
    def set(
        self,
        key: ConfigurationKey,
        value: Any,
    ) -> ConfigurationValue:
        """
        Store or update a configuration value.
        """

        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Delete a configuration value.
        """

        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Determine whether a configuration value exists.
        """

        raise NotImplementedError


class ConfigurationRegistry(ABC):
    """
    Contract for configuration definitions.
    """

    @abstractmethod
    def register(
        self,
        definition: ConfigurationDefinition,
    ) -> None:
        """
        Register a configuration definition.
        """

        raise NotImplementedError

    @abstractmethod
    def get_definition(
        self,
        name: str,
    ) -> Optional[ConfigurationDefinition]:
        """
        Retrieve a configuration definition.
        """

        raise NotImplementedError

    @abstractmethod
    def definitions(
        self,
    ) -> Iterable[ConfigurationDefinition]:
        """
        Return registered definitions.
        """

        raise NotImplementedError


class ConfigurationResolver(ABC):
    """
    Contract for resolving configuration values
    across configuration scopes.
    """

    @abstractmethod
    def resolve(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:
        """
        Resolve the effective configuration value.
        """

        raise NotImplementedError


__all__ = [
    "ConfigurationProvider",
    "ConfigurationRegistry",
    "ConfigurationResolver",
]
