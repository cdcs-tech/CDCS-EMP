"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Provider-neutral analytics and KPI contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ReportKPIValueType(str, Enum):
    """
    Supported provider-neutral KPI value types.

    The value type describes the semantic type of a KPI
    result without prescribing how the value is calculated,
    stored, queried, or presented.
    """

    INTEGER = "integer"

    DECIMAL = "decimal"

    PERCENTAGE = "percentage"

    CURRENCY = "currency"

    RATIO = "ratio"

    BOOLEAN = "boolean"

    TEXT = "text"


@dataclass(frozen=True)
class ReportKPI:
    """
    Represents a provider-neutral KPI definition.

    A KPI definition describes what a key performance indicator
    represents without defining how its value is calculated.

    KPI calculation, aggregation, query execution, persistence,
    presentation, authorization, auditing, governance, and
    telemetry remain outside this contract.
    """

    code: str

    name: str

    description: str | None = None

    value_type: ReportKPIValueType = (
        ReportKPIValueType.DECIMAL
    )

    unit: str | None = None

    category: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    active: bool = True

    def __post_init__(self) -> None:
        """
        Validate and normalize the KPI definition.
        """

        if not isinstance(
            self.code,
            str,
        ):
            raise ValueError(
                "Report KPI code must be a string."
            )

        normalized_code = self.code.strip()

        if not normalized_code:
            raise ValueError(
                "Report KPI code is required."
            )

        object.__setattr__(
            self,
            "code",
            normalized_code,
        )

        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "Report KPI name must be a string."
            )

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "Report KPI name is required."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

        if self.description is not None:

            if not isinstance(
                self.description,
                str,
            ):
                raise ValueError(
                    "Report KPI description must be a "
                    "string or None."
                )

            normalized_description = (
                self.description.strip()
            )

            if not normalized_description:
                object.__setattr__(
                    self,
                    "description",
                    None,
                )
            else:
                object.__setattr__(
                    self,
                    "description",
                    normalized_description,
                )

        value_type = self.value_type

        if isinstance(
            value_type,
            str,
        ):
            normalized_value_type = (
                value_type.strip().lower()
            )

            try:
                value_type = ReportKPIValueType(
                    normalized_value_type
                )
            except ValueError as exc:
                raise ValueError(
                    "Invalid Report KPI value_type "
                    f"'{normalized_value_type}'."
                ) from exc

            object.__setattr__(
                self,
                "value_type",
                value_type,
            )

        elif not isinstance(
            value_type,
            ReportKPIValueType,
        ):
            raise ValueError(
                "Report KPI value_type must be a "
                "ReportKPIValueType."
            )

        if self.unit is not None:

            if not isinstance(
                self.unit,
                str,
            ):
                raise ValueError(
                    "Report KPI unit must be a string "
                    "or None."
                )

            normalized_unit = self.unit.strip()

            if not normalized_unit:
                object.__setattr__(
                    self,
                    "unit",
                    None,
                )
            else:
                object.__setattr__(
                    self,
                    "unit",
                    normalized_unit,
                )

        if self.category is not None:

            if not isinstance(
                self.category,
                str,
            ):
                raise ValueError(
                    "Report KPI category must be a string "
                    "or None."
                )

            normalized_category = (
                self.category.strip()
            )

            if not normalized_category:
                object.__setattr__(
                    self,
                    "category",
                    None,
                )
            else:
                object.__setattr__(
                    self,
                    "category",
                    normalized_category,
                )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report KPI metadata must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

        if not isinstance(
            self.active,
            bool,
        ):
            raise ValueError(
                "Report KPI active flag must be a boolean."
            )

    @property
    def identifier(self) -> str:
        """
        Return the canonical KPI identifier.

        KPI identifiers are represented by their normalized
        KPI code in uppercase form.
        """

        return self.code.upper()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the KPI definition into a stable,
        provider-neutral dictionary representation.
        """

        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "value_type": self.value_type.value,
            "unit": self.unit,
            "category": self.category,
            "metadata": dict(
                self.metadata
            ),
            "active": self.active,
        }


__all__ = [
    "ReportKPIValueType",
    "ReportKPI",
]
