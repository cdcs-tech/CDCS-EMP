"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Application service container.
"""

from __future__ import annotations

from typing import Any, Dict

from app.core.services.exceptions import (
    ServiceException,
)


class ServiceContainerException(
    ServiceException
):
    """
    Base exception for service container failures.
    """


class ServiceAlreadyRegisteredException(
    ServiceContainerException
):
    """
    Raised when a service is already registered.
    """


class ServiceNotRegisteredException(
    ServiceContainerException
):
    """
    Raised when a requested service is not registered.
    """


class ServiceContainer:
    """
    Application-scoped dependency injection container.

    The container manages initialized enterprise service
    instances during the application lifecycle.
    """

    EXTENSION_KEY = "service_container"

    def __init__(self) -> None:
        """
        Initialize the service container.
        """

        self._services: Dict[
            str,
            Any,
        ] = {}

    def register(
        self,
        name: str,
        service: Any,
        *,
        replace: bool = False,
    ) -> None:
        """
        Register a service instance.

        Args:
            name:
                Unique service name.

            service:
                Initialized service instance.

            replace:
                Whether an existing registration may be
                replaced explicitly.
        """

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise ServiceContainerException(
                "Service name is required."
            )

        if service is None:
            raise ServiceContainerException(
                f"Service '{name}' cannot be None."
            )

        name = name.strip()

        if (
            name in self._services
            and not replace
        ):
            raise ServiceAlreadyRegisteredException(
                f"Service '{name}' is already registered."
            )

        self._services[name] = service

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a registered service.

        Raises:
            ServiceNotRegisteredException:
                If the service is not registered.
        """

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise ServiceContainerException(
                "Service name is required."
            )

        name = name.strip()

        if name not in self._services:
            raise ServiceNotRegisteredException(
                f"Service '{name}' is not registered."
            )

        return self._services[name]

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Determine whether a service is registered.
        """

        if not isinstance(
            name,
            str,
        ):
            return False

        return name.strip() in self._services

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a service registration.

        Raises:
            ServiceNotRegisteredException:
                If the service does not exist.
        """

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise ServiceContainerException(
                "Service name is required."
            )

        name = name.strip()

        if name not in self._services:
            raise ServiceNotRegisteredException(
                f"Service '{name}' is not registered."
            )

        del self._services[name]

    def clear(
        self,
    ) -> None:
        """
        Remove all registered services.
        """

        self._services.clear()

    def all(
        self,
    ) -> Dict[str, Any]:
        """
        Return a copy of all registered services.
        """

        return dict(
            self._services
        )

    def names(
        self,
    ) -> list[str]:
        """
        Return registered service names.
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

    @classmethod
    def from_app(
        cls,
        app,
    ) -> "ServiceContainer":
        """
        Resolve the application service container.

        The container is expected to be exposed through
        Flask's application extensions registry.
        """

        container = app.extensions.get(
            cls.EXTENSION_KEY
        )

        if container is None:
            raise ServiceContainerException(
                "Application service container "
                "is not registered."
            )

        if not isinstance(
            container,
            cls,
        ):
            raise ServiceContainerException(
                "Registered application service container "
                "has an invalid type."
            )

        return container

    def register_with_app(
        self,
        app,
    ) -> None:
        """
        Register this container with a Flask application.
        """

        if app is None:
            raise ServiceContainerException(
                "Flask application is required."
            )

        app.extensions[
            self.EXTENSION_KEY
        ] = self

    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Support membership testing.
        """

        return self.has(
            name
        )

    def __iter__(
        self,
    ):
        """
        Iterate over registered service names.
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
            f"<ServiceContainer "
            f"{self.count()} services>"
        )


service_container = ServiceContainer()


__all__ = [
    "ServiceContainerException",
    "ServiceAlreadyRegisteredException",
    "ServiceNotRegisteredException",
    "ServiceContainer",
    "service_container",
]
