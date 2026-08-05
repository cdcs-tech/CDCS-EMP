"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Dependency injection container.
"""


from __future__ import annotations


from typing import (
    Any,
    Dict,
)



class ServiceContainer:
    """
    Lightweight dependency injection container.

    Manages service instances during
    application runtime.
    """


    def __init__(
        self,
    ):
        """
        Initialize container.
        """

        self._services: Dict[
            str,
            Any,
        ] = {}



    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Register service instance.
        """

        self._services[name] = service



    def resolve(
        self,
        name: str,
    ) -> Any | None:
        """
        Resolve service instance.
        """

        return self._services.get(
            name
        )



    def has(
        self,
        name: str,
    ) -> bool:
        """
        Check whether service exists.
        """

        return name in self._services



    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove service registration.
        """

        self._services.pop(
            name,
            None,
        )



    def clear(
        self,
    ) -> None:
        """
        Clear all services.
        """

        self._services.clear()



    def count(
        self,
    ) -> int:
        """
        Return registered service count.
        """

        return len(
            self._services
        )



service_container = ServiceContainer()
