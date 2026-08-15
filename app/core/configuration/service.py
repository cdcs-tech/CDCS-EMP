"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Configuration Framework

Configuration service contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.configuration.domain import (
    ConfigurationDefinition,
    ConfigurationKey,
    ConfigurationValue,
)
from app.core.configuration.resolution import (
    ConfigurationResolutionContext,
)


class ConfigurationService(ABC):
    """
    Abstract application-facing configuration service.

    The configuration service coordinates configuration
    retrieval, storage, definition management, and
    effective-value resolution.

    Concrete implementations are responsible for
    composing the underlying provider, registry,
    resolver, and validation components.
    """

    @abstractmethod
    def get(
        self,
        key: ConfigurationKey,
    ) -> Optional[ConfigurationValue]:
        """
        Retrieve a configuration value.

        Returns:
            The stored configuration value, or None
            when no value exists.
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

        Returns:
            The resulting configuration value.
        """

        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        key: ConfigurationKey,
    ) -> bool:
        """
        Delete a configuration value.

        Returns:
            True when a value was deleted,
            otherwise False.
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
    def register_definition(
        self,
        definition: ConfigurationDefinition,
    ) -> None:
        """
        Register a configuration definition.
        """

        raise NotImplementedError

    @abstractmethod
    def resolve(
        self,
        key: str,
        context: ConfigurationResolutionContext,
        default: Any = None,
        definition: Optional[
            ConfigurationDefinition
        ] = None,
    ) -> Any:
        """
        Resolve the effective configuration value
        for the supplied context.

        Resolution and validation remain separate
        responsibilities behind the service boundary.
        """

        raise NotImplementedError


__all__ = [
    "ConfigurationService",
]
