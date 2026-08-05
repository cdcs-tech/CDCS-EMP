"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

CRUD configuration definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from typing import List


@dataclass
class CRUDConfig:
    """
    Defines CRUD behaviour configuration
    for an enterprise entity.
    """

    module_name: str

    entity_name: str

    display_name: str | None = None

    enable_create: bool = True

    enable_read: bool = True

    enable_update: bool = True

    enable_delete: bool = True

    permissions: List[str] = field(
        default_factory=list
    )

    list_columns: List[str] = field(
        default_factory=list
    )


    def get_display_name(
        self,
    ) -> str:
        """
        Return entity display name.
        """

        return (
            self.display_name
            or self.entity_name
        )


    def enabled_operations(
        self,
    ) -> list[str]:
        """
        Return enabled CRUD operations.
        """

        operations = []


        if self.enable_create:
            operations.append(
                "create"
            )


        if self.enable_read:
            operations.append(
                "read"
            )


        if self.enable_update:
            operations.append(
                "update"
            )


        if self.enable_delete:
            operations.append(
                "delete"
            )


        return operations
