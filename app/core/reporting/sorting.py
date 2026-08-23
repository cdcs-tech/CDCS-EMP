"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Provider-neutral reporting sorting contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator


class ReportSortDirection(str, Enum):
    """
    Supported provider-neutral report sort directions.
    """

    ASCENDING = "asc"
    DESCENDING = "desc"


@dataclass(frozen=True)
class ReportSort:
    """
    Represents a single provider-neutral report sort.

    A report sort describes the semantic ordering
    requirement without prescribing how the underlying
    data provider must implement it.
    """

    field: str

    direction: ReportSortDirection = (
        ReportSortDirection.ASCENDING
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the sort definition.
        """

        if not isinstance(
            self.field,
            str,
        ):
            raise ValueError(
                "Report sort field must be a string."
            )

        normalized_field = self.field.strip()

        if not normalized_field:
            raise ValueError(
                "Report sort field is required."
            )

        object.__setattr__(
            self,
            "field",
            normalized_field,
        )

        direction = self.direction

        if isinstance(
            direction,
            str,
        ):
            try:
                direction = ReportSortDirection(
                    direction.strip().lower()
                )
            except ValueError as exc:
                raise ValueError(
                    "Invalid report sort direction."
                ) from exc

            object.__setattr__(
                self,
                "direction",
                direction,
            )

        elif not isinstance(
            direction,
            ReportSortDirection,
        ):
            raise ValueError(
                "Report sort direction must be a "
                "ReportSortDirection."
            )

    def to_dict(self) -> dict[str, str]:
        """
        Serialize the sort definition.
        """

        return {
            "field": self.field,
            "direction": self.direction.value,
        }


@dataclass
class ReportSortCollection:
    """
    Ordered collection of report sort definitions.

    Sort order is significant. The first sort definition
    represents the primary ordering criterion, followed by
    subsequent definitions as secondary ordering criteria.
    """

    sorts: list[ReportSort] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        """
        Validate the initial sort collection.
        """

        normalized: list[ReportSort] = []

        for report_sort in self.sorts:

            if not isinstance(
                report_sort,
                ReportSort,
            ):
                raise ValueError(
                    "Report sort collection must contain "
                    "ReportSort instances."
                )

            normalized.append(
                report_sort
            )

        self.sorts = normalized

    def add(
        self,
        report_sort: ReportSort,
    ) -> None:
        """
        Add a report sort definition.

        Raises:
            ValueError:
                When the supplied value is invalid or
                a sort for the same field already exists.
        """

        if not isinstance(
            report_sort,
            ReportSort,
        ):
            raise ValueError(
                "report_sort must be a ReportSort instance."
            )

        if self.contains(
            report_sort.field
        ):
            raise ValueError(
                f"Report sort for field "
                f"'{report_sort.field}' is already defined."
            )

        self.sorts.append(
            report_sort
        )

    def get(
        self,
        field: str,
    ) -> ReportSort:
        """
        Retrieve a sort definition by field.

        Raises:
            KeyError:
                When no sort exists for the field.
        """

        normalized_field = field.strip()

        for report_sort in self.sorts:

            if report_sort.field == normalized_field:
                return report_sort

        raise KeyError(
            f"Report sort for field "
            f"'{normalized_field}' is not defined."
        )

    def contains(
        self,
        field: str,
    ) -> bool:
        """
        Determine whether a sort exists for a field.
        """

        normalized_field = field.strip()

        return any(
            report_sort.field
            == normalized_field
            for report_sort in self.sorts
        )

    def remove(
        self,
        field: str,
    ) -> None:
        """
        Remove a sort definition by field.

        Raises:
            KeyError:
                When no sort exists for the field.
        """

        normalized_field = field.strip()

        for index, report_sort in enumerate(
            self.sorts
        ):

            if report_sort.field == normalized_field:

                del self.sorts[index]

                return

        raise KeyError(
            f"Report sort for field "
            f"'{normalized_field}' is not defined."
        )

    def clear(self) -> None:
        """
        Remove all report sort definitions.
        """

        self.sorts.clear()

    def count(self) -> int:
        """
        Return the number of report sort definitions.
        """

        return len(
            self.sorts
        )

    def to_list(self) -> list[dict[str, str]]:
        """
        Serialize all report sort definitions.

        The original ordering is preserved because sort
        precedence is semantically significant.
        """

        return [
            report_sort.to_dict()
            for report_sort in self.sorts
        ]

    def __len__(self) -> int:
        return len(
            self.sorts
        )

    def __iter__(
        self,
    ) -> Iterator[ReportSort]:
        return iter(
            self.sorts
        )

    def __contains__(
        self,
        field: str,
    ) -> bool:
        return self.contains(
            field
        )


__all__ = [
    "ReportSortDirection",
    "ReportSort",
    "ReportSortCollection",
]
