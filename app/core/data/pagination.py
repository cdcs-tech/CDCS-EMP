"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Reusable pagination models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Generic, List, TypeVar

from app.core.data.entity import BaseEntity

TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


@dataclass(frozen=True)
class Pagination:
    """
    Represents pagination request settings.
    """

    page: int = 1

    page_size: int = 25


@dataclass
class PaginatedResult(
    Generic[TEntity],
):
    """
    Represents a paginated collection of
    enterprise entities.
    """

    items: List[TEntity] = field(
        default_factory=list
    )

    total_records: int = 0

    page: int = 1

    page_size: int = 25

    @property
    def total_pages(self) -> int:
        """
        Calculate total pages.
        """

        if self.page_size <= 0:
            return 0

        return ceil(
            self.total_records /
            self.page_size
        )

    @property
    def has_previous(self) -> bool:
        """
        Determine whether a previous page exists.
        """

        return self.page > 1

    @property
    def has_next(self) -> bool:
        """
        Determine whether a next page exists.
        """

        return self.page < self.total_pages

    def to_dict(self):
        """
        Convert pagination result into a
        serializable dictionary.
        """

        return {

            "page": self.page,

            "page_size": self.page_size,

            "total_records": self.total_records,

            "total_pages": self.total_pages,

            "has_previous": self.has_previous,

            "has_next": self.has_next,

            "items": [
                item.to_dict()
                for item in self.items
            ],
        }
