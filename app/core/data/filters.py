"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Reusable filtering models.
"""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass(frozen=True)
class Filter:
    """
    Represents a single filter condition.
    """

    field: str

    operator: str

    value: Any


@dataclass
class FilterCollection:
    """
    Collection of reusable filter definitions.
    """

    filters: List[Filter] = field(
        default_factory=list
    )

    def add(
        self,
        field: str,
        operator: str,
        value: Any,
    ) -> None:
        """
        Add a filter definition.
        """

        self.filters.append(
            Filter(
                field=field,
                operator=operator,
                value=value,
            )
        )

    def clear(self) -> None:
        """
        Remove all filters.
        """

        self.filters.clear()

    def __len__(self) -> int:
        return len(self.filters)

    def __iter__(self):
        return iter(self.filters)

    def to_list(self) -> List[dict]:
        """
        Convert filters into a serializable list.
        """

        return [
            {
                "field": item.field,
                "operator": item.operator,
                "value": item.value,
            }
            for item in self.filters
        ]
