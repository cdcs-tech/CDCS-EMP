"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Service registry implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class ServiceRegistryException(Exception):
    """
    Base exception for service registry operations.
    """


class ServiceDefinitionException(
    ServiceRegistryException
):
    """
    Raised when a service definition is invalid.
    """


class ServiceRegistrationException(
    ServiceRegistryException
):
    """
    Raised when service registration fails.
    """


class ServiceResolutionException(
    ServiceRegistryException
):
    """
    Raised when a registered service cannot be resolved.
    """


@dataclass
class ServiceDefinition:
    """
    Defines a registered enterprise service.
    """

    module_name: str

    service_name: str

    service_class: Any | None = None

    instance: Any | None = None

    def __post_init__(self) -> None:
        """
        Normalize and validate the service definition.
        """

        if not isinstance(
            self.module_name,
            str,
        ):
            raise ServiceDefinitionException(
                "Service module name must be a string."
            )

        if not isinstance(
            self.service_name,
            str,
        ):
            raise ServiceDefinitionException(
                "Service name must be a string."
            )

        self.module_name = (
            self.module_name.strip()
        )

        self.service_name = (
            self.service_name.strip()
        )

        if not self.module_name:
            raise ServiceDefinitionException(
                "Service module name is required."
            )

        if not self.service_name:
            raise ServiceDefinitionException(
                "Service name is required."
            )

    @property
    def key(self) -> str:
        """
        Return the canonical service registry key.
        """

        return (
            f"{self.module_name}."
            f"{self.service_name}"
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Return a serializable representation.
        """

        return {
            "module_name": self.module_name,
            "service_name": self.service_name,
            "key": self.key,
            "service_class": (
                self.service_class.__name__
                if self.service_class is not None
                else None
            ),
            "instance": (
                type(self.instance).__name__
                if self.instance is not None
                else None
            ),
        }


class ServiceRegistry:
    """
    Central registry for enterprise services.

    The registry maintains service definitions.
    Runtime service instances are managed by the
    ServiceContainer.
    """

    def __init__(self) -> None:
        """
        Initialize the registry.
        """

        self._services: Dict[
            str,
            ServiceDefinition,
        ] = {}

    def register(
        self,
        definition: ServiceDefinition,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a service definition.

        Duplicate registrations are rejected unless
        ``replace=True`` is explicitly supplied.
        """

        if not isinstance(
            definition,
            ServiceDefinition,
        ):
            raise ServiceDefinitionException(
                "Service definition must be a "
                "ServiceDefinition instance."
            )

        key = definition.key

        if (
            key in self._services
            and not replace
        ):
            raise ServiceRegistrationException(
                f"Service '{key}' is already registered."
            )

        self._services[key] = definition

    def get(
        self,
        module_name: str,
        service_name: str,
    ) -> ServiceDefinition:
        """
        Retrieve a registered service definition.

        Raises ServiceResolutionException when the
        service is not registered.
        """

        key = self._build_key(
            module_name,
            service_name,
        )

        if key not in self._services:
            raise ServiceResolutionException(
                f"Service '{key}' is not registered."
            )

        return self._services[key]

    def has(
        self,
        module_name: str,
        service_name: str,
    ) -> bool:
        """
        Determine whether a service is registered.
        """

        key = self._build_key(
            module_name,
            service_name,
        )

        return key in self._services

    def remove(
        self,
        module_name: str,
        service_name: str,
    ) -> None:
        """
        Remove a registered service definition.
        """

        key = self._build_key(
            module_name,
            service_name,
        )

        if key not in self._services:
            raise ServiceResolutionException(
                f"Service '{key}' is not registered."
            )

        del self._services[key]

    def all(
        self,
    ) -> list[ServiceDefinition]:
        """
        Return all registered service definitions.

        A new list is returned so callers cannot mutate
        the registry collection directly.
        """

        return list(
            self._services.values()
        )

    def names(
        self,
    ) -> list[str]:
        """
        Return all registered service keys.
        """

        return list(
            self._services.keys()
        )

    def count(
        self,
    ) -> int:
        """
        Return the number of registered services.
        """

        return len(
            self._services
        )

    def clear(
        self,
    ) -> None:
        """
        Remove all service definitions.
        """

        self._services.clear()

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Support membership testing by service key.
        """

        return key in self._services

    def __iter__(self):
        """
        Iterate over registered service keys.
        """

        return iter(
            self._services
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<ServiceRegistry "
            f"{self.count()} services>"
        )

    @staticmethod
    def _build_key(
        module_name: str,
        service_name: str,
    ) -> str:
        """
        Build and validate a canonical service key.
        """

        if not isinstance(
            module_name,
            str,
        ):
            raise ServiceDefinitionException(
                "Service module name must be a string."
            )

        if not isinstance(
            service_name,
            str,
        ):
            raise ServiceDefinitionException(
                "Service name must be a string."
            )

        module_name = (
            module_name.strip()
        )

        service_name = (
            service_name.strip()
        )

        if not module_name:
            raise ServiceDefinitionException(
                "Service module name is required."
            )

        if not service_name:
            raise ServiceDefinitionException(
                "Service name is required."
            )

        return (
            f"{module_name}."
            f"{service_name}"
        )


service_registry = ServiceRegistry()


__all__ = [
    "ServiceRegistryException",
    "ServiceDefinitionException",
    "ServiceRegistrationException",
    "ServiceResolutionException",
    "ServiceDefinition",
    "ServiceRegistry",
    "service_registry",
]
