"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Reusable query models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class QueryOptions:
    """
    Encapsulates query parameters used by
    repositories and services.

    QueryOptions is responsible only for framework-level
    query validation and normalization. Model-specific
    field resolution remains the responsibility of the
    repository/query execution layer.
    """

    page: int = 1

    page_size: int = 25

    sort_by: str = "id"

    sort_direction: str = "asc"

    filters: Dict[str, Any] = field(
        default_factory=dict
    )

    search: str | None = None

    fields: List[str] = field(
        default_factory=list
    )

    include_inactive: bool = False

    def __post_init__(self) -> None:
        """
        Validate and normalize query options immediately
        after construction.
        """

        self._validate_page()

        self._validate_page_size()

        self._normalize_sort_by()

        self._normalize_sort_direction()

        self._normalize_search()

        self._normalize_fields()

    def _validate_page(self) -> None:
        """
        Validate the requested page number.

        Raises:
            ValueError:
                When page is less than one.
        """

        if self.page < 1:
            raise ValueError(
                "page must be greater than or equal to 1."
            )

    def _validate_page_size(self) -> None:
        """
        Validate the requested page size.

        Raises:
            ValueError:
                When page_size is less than one.
        """

        if self.page_size < 1:
            raise ValueError(
                "page_size must be greater than or equal to 1."
            )

    def _normalize_sort_by(self) -> None:
        """
        Normalize the sort field.

        Raises:
            ValueError:
                When sort_by is empty after normalization.
        """

        if self.sort_by is None:
            raise ValueError(
                "sort_by is required."
            )

        self.sort_by = self.sort_by.strip()

        if not self.sort_by:
            raise ValueError(
                "sort_by must not be empty."
            )

    def _normalize_sort_direction(self) -> None:
        """
        Normalize and validate sort direction.

        Supported values are:
            asc
            desc

        Raises:
            ValueError:
                When an unsupported direction is supplied.
        """

        if self.sort_direction is None:
            raise ValueError(
                "sort_direction is required."
            )

        self.sort_direction = (
            self.sort_direction.strip().lower()
        )

        if self.sort_direction not in {
            "asc",
            "desc",
        }:
            raise ValueError(
                "sort_direction must be 'asc' or 'desc'."
            )

    def _normalize_search(self) -> None:
        """
        Normalize the optional search value.

        Blank search values are represented as None.
        """

        if self.search is None:
            return

        self.search = self.search.strip()

        if not self.search:
            self.search = None

    def _normalize_fields(self) -> None:
        """
        Normalize requested field names.

        Field names are stripped of surrounding whitespace.
        Blank field names are rejected.
        """

        normalized_fields: List[str] = []

        for field_name in self.fields:

            if field_name is None:
                raise ValueError(
                    "fields must not contain empty field names."
                )

            normalized_field = field_name.strip()

            if not normalized_field:
                raise ValueError(
                    "fields must not contain empty field names."
                )

            normalized_fields.append(
                normalized_field
            )

        self.fields = normalized_fields

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert query options to a dictionary.

        Mutable collections are copied so callers cannot
        mutate the QueryOptions instance through the
        serialized representation.
        """

        return {
            "page": self.page,
            "page_size": self.page_size,
            "sort_by": self.sort_by,
            "sort_direction": self.sort_direction,
            "filters": dict(self.filters),
            "search": self.search,
            "fields": list(self.fields),
            "include_inactive": self.include_inactive,
        }


__all__ = [
    "QueryOptions",
]
