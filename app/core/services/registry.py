"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Services Framework

Service registry implementation.
"""


from __future__ import annotations


from dataclasses import dataclass


from typing import (
    Any,
    Dict,
)



@dataclass
class ServiceDefinition:
    """
    Defines a registered service.
    """

    module_name: str

    service_name: str

    service_class: Any | None = None

    instance: Any | None = None



class ServiceRegistry:
    """
    Central registry for enterprise services.
    """


    def __init__(
        self,
    ):
        """
        Initialize registry.
        """

        self._services: Dict[
            str,
            ServiceDefinition,
        ] = {}



    def register(
        self,
        definition: ServiceDefinition,
    ) -> None:
        """
        Register a service definition.
        """

        key = (
            f"{definition.module_name}."
            f"{definition.service_name}"
        )


        self._services[key] = definition



    def get(
        self,
        module_name: str,
        service_name: str,
    ) -> ServiceDefinition | None:
        """
        Retrieve service definition.
        """

        key = (
            f"{module_name}."
            f"{service_name}"
        )


        return self._services.get(
            key
        )



    def all(
        self,
    ) -> list[ServiceDefinition]:
        """
        Return all registered services.
        """

        return list(
            self._services.values()
        )



    def count(
        self,
    ) -> int:
        """
        Return number of registered services.
        """

        return len(
            self._services
        )



service_registry = ServiceRegistry()
