"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

CRUD registration registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class CRUDDefinition:
    """
    Defines a registered CRUD entity.
    """

    module_name: str

    entity_name: str

    service: Any | None = None

    repository: Any | None = None

    view: Any | None = None

    form: Any | None = None

    table: Any | None = None



class CRUDRegistry:
    """
    Central registry for CRUD definitions.
    """

    def __init__(self):

        self._definitions: Dict[
            str,
            CRUDDefinition
        ] = {}


    def register(
        self,
        definition: CRUDDefinition,
    ) -> None:
        """
        Register CRUD definition.
        """

        key = (
            f"{definition.module_name}."
            f"{definition.entity_name}"
        )

        self._definitions[key] = definition


    def get(
        self,
        module_name: str,
        entity_name: str,
    ) -> CRUDDefinition | None:
        """
        Retrieve CRUD definition.
        """

        key = (
            f"{module_name}."
            f"{entity_name}"
        )

        return self._definitions.get(
            key
        )


    def all(
        self,
    ):
        """
        Return all definitions.
        """

        return list(
            self._definitions.values()
        )


    def count(
        self,
    ) -> int:
        """
        Return registered definition count.
        """

        return len(
            self._definitions
        )


crud_registry = CRUDRegistry()
