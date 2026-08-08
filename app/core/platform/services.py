"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure

Platform Service Container.

Provides centralized registration and
resolution of reusable platform services.
"""

from typing import Any, Iterator


class ServiceRegistrationException(
    Exception
):
    """
    Raised when service registration fails.
    """


class ServiceResolutionException(
    Exception
):
    """
    Raised when a service cannot be resolved.
    """


class PlatformServiceContainer:
    """
    Central registry and resolver for platform services.
    """

    def __init__(self):
        """
        Initialize the service container.
        """

        self._services: dict[
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
        Register a platform service.
        """

        if not name:
            raise ServiceRegistrationException(
                "Service name is required."
            )

        if service is None:
            raise ServiceRegistrationException(
                f"Service '{name}' cannot be None."
            )

        if (
            name in self._services
            and not replace
        ):
            raise ServiceRegistrationException(
                f"Service '{name}' is already registered."
            )

        self._services[name] = service


    def get(
        self,
        name: str,
    ) -> Any:
        """
        Resolve a registered service.
        """

        if name not in self._services:
            raise ServiceResolutionException(
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

        return name in self._services


    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a registered service.
        """

        if name not in self._services:
            raise ServiceResolutionException(
                f"Service '{name}' is not registered."
            )

        del self._services[name]


    def all(self) -> dict[str, Any]:
        """
        Return a copy of all registered services.
        """

        return dict(
            self._services
        )


    def names(self) -> list[str]:
        """
        Return registered service names.
        """

        return list(
            self._services.keys()
        )


    def count(self) -> int:
        """
        Return the number of registered services.
        """

        return len(
            self._services
        )


    def clear(self) -> None:
        """
        Remove all registered services.
        """

        self._services.clear()


    def __contains__(
        self,
        name: str,
    ) -> bool:
        """
        Support membership testing.
        """

        return name in self._services


    def __iter__(
        self,
    ) -> Iterator[str]:
        """
        Iterate over service names.
        """

        return iter(
            self._services
        )


    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """

        return (
            f"<PlatformServiceContainer "
            f"{self.count()} services>"
        )


platform_services = (
    PlatformServiceContainer()
)


__all__ = [
    "ServiceRegistrationException",
    "ServiceResolutionException",
    "PlatformServiceContainer",
    "platform_services",
]
