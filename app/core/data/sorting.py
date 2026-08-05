"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Reusable sorting models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class SortDirection(str, Enum):
    """
    Supported sort directions.
    """

    ASCENDING = "asc"
    DESCENDING = "desc"


@dataclass(frozen=True)
class SortDefinition:
    """
    Represents a single sort definition.
    """

    field: str

    direction: SortDirection = (
        SortDirection.ASCENDING
    )


@dataclass
class SortCollection:
    """
    Collection of sort definitions.
    """

    sorts: List[SortDefinition] = field(
        default_factory=list
    )

    def add(
        self,
        field: str,
        direction: SortDirection = (
            SortDirection.ASCENDING
        ),
    ) -> None:
        """
        Add a sort definition.
        """

        self.sorts.append(
            SortDefinition(
                field=field,
                direction=direction,
            )
        )

    def clear(self) -> None:
        """
        Remove all sort definitions.
        """

        self.sorts.clear()

    def __len__(self) -> int:
        return len(self.sorts)

    def __iter__(self):
        return iter(self.sorts)

    def to_list(self) -> List[dict]:
        """
        Convert sort definitions into a
        serializable list.
        """

        return [
            {
                "field": item.field,
                "direction": item.direction.value,
            }
            for item in self.sorts
        ]
