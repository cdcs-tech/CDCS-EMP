"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Provider-neutral reporting filter contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator


class ReportFilterOperator(str, Enum):
    """
    Supported provider-neutral reporting filter operators.
    """

    EQUALS = "eq"
    NOT_EQUALS = "neq"

    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"

    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"

    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"

    IN = "in"
    NOT_IN = "not_in"

    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


@dataclass(frozen=True)
class ReportFilter:
    """
    Represents a single provider-neutral report filter.

    A report filter describes the semantic filtering
    requirement without prescribing how the underlying
    data provider must implement it.
    """

    field: str
    operator: ReportFilterOperator
    value: Any = None

    def __post_init__(self) -> None:
        """
        Validate and normalize the filter contract.
        """

        if not isinstance(
            self.field,
            str,
        ):
            raise ValueError(
                "Report filter field must be a string."
            )

        normalized_field = self.field.strip()

        if not normalized_field:
            raise ValueError(
                "Report filter field is required."
            )

        object.__setattr__(
            self,
            "field",
            normalized_field,
        )

        operator = self.operator

        if isinstance(
            operator,
            str,
        ):
            try:
                operator = (
                    ReportFilterOperator(
                        operator.strip().lower()
                    )
                )
            except ValueError as exc:
                raise ValueError(
                    "Invalid report filter operator."
                ) from exc

            object.__setattr__(
                self,
                "operator",
                operator,
            )

        elif not isinstance(
            operator,
            ReportFilterOperator,
        ):
            raise ValueError(
                "Report filter operator must be a "
                "ReportFilterOperator."
            )

        if operator in (
            ReportFilterOperator.IS_NULL,
            ReportFilterOperator.IS_NOT_NULL,
        ):
            if self.value is not None:
                raise ValueError(
                    f"Report filter operator "
                    f"'{operator.value}' does not accept "
                    "a filter value."
                )

    @property
    def requires_value(self) -> bool:
        """
        Determine whether the operator requires a value.
        """

        return self.operator not in (
            ReportFilterOperator.IS_NULL,
            ReportFilterOperator.IS_NOT_NULL,
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the filter contract.
        """

        return {
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value,
        }


@dataclass
class ReportFilterCollection:
    """
    Ordered collection of report filters.

    The collection provides a stable provider-neutral
    contract for composing multiple report filters.
    """

    filters: list[ReportFilter] = field(
        default_factory=list
    )

    def __post_init__(self) -> None:
        """
        Validate the initial filter collection.
        """

        normalized: list[ReportFilter] = []

        for report_filter in self.filters:

            if not isinstance(
                report_filter,
                ReportFilter,
            ):
                raise ValueError(
                    "Report filter collection must contain "
                    "ReportFilter instances."
                )

            normalized.append(
                report_filter
            )

        self.filters = normalized

    def add(
        self,
        report_filter: ReportFilter,
    ) -> None:
        """
        Add a report filter.

        Raises:
            ValueError:
                When the supplied value is invalid or
                a filter for the same field already exists.
        """

        if not isinstance(
            report_filter,
            ReportFilter,
        ):
            raise ValueError(
                "report_filter must be a ReportFilter instance."
            )

        if self.contains(
            report_filter.field
        ):
            raise ValueError(
                f"Report filter for field "
                f"'{report_filter.field}' is already defined."
            )

        self.filters.append(
            report_filter
        )

    def get(
        self,
        field: str,
    ) -> ReportFilter:
        """
        Retrieve a filter by field.

        Raises:
            KeyError:
                When no filter exists for the field.
        """

        normalized_field = field.strip()

        for report_filter in self.filters:

            if report_filter.field == normalized_field:
                return report_filter

        raise KeyError(
            f"Report filter for field "
            f"'{normalized_field}' is not defined."
        )

    def contains(
        self,
        field: str,
    ) -> bool:
        """
        Determine whether a filter exists for a field.
        """

        normalized_field = field.strip()

        return any(
            report_filter.field
            == normalized_field
            for report_filter in self.filters
        )

    def remove(
        self,
        field: str,
    ) -> None:
        """
        Remove a filter by field.

        Raises:
            KeyError:
                When no filter exists for the field.
        """

        normalized_field = field.strip()

        for index, report_filter in enumerate(
            self.filters
        ):

            if report_filter.field == normalized_field:

                del self.filters[index]

                return

        raise KeyError(
            f"Report filter for field "
            f"'{normalized_field}' is not defined."
        )

    def clear(self) -> None:
        """
        Remove all report filters.
        """

        self.filters.clear()

    def count(self) -> int:
        """
        Return the number of report filters.
        """

        return len(
            self.filters
        )

    def to_list(self) -> list[dict[str, Any]]:
        """
        Serialize all report filters.
        """

        return [
            report_filter.to_dict()
            for report_filter in self.filters
        ]

    def __len__(self) -> int:
        return len(
            self.filters
        )

    def __iter__(
        self,
    ) -> Iterator[ReportFilter]:
        return iter(
            self.filters
        )

    def __contains__(
        self,
        field: str,
    ) -> bool:
        return self.contains(
            field
        )


__all__ = [
    "ReportFilterOperator",
    "ReportFilter",
    "ReportFilterCollection",
]
