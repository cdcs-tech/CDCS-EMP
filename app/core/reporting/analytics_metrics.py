"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Provider-neutral analytics metric and aggregation contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AnalyticsAggregationType(str, Enum):
    """
    Supported provider-neutral analytics aggregation types.

    The aggregation type describes the mathematical operation
    requested for an analytics metric without prescribing how
    the operation is executed by a data provider.
    """

    COUNT = "count"

    SUM = "sum"

    AVERAGE = "average"

    MINIMUM = "minimum"

    MAXIMUM = "maximum"

    @classmethod
    def normalize(
        cls,
        value: AnalyticsAggregationType | str,
    ) -> AnalyticsAggregationType:
        """
        Normalize an aggregation type value into an
        AnalyticsAggregationType instance.

        Args:
            value:
                An AnalyticsAggregationType instance or
                supported string representation.

        Returns:
            AnalyticsAggregationType:
                The normalized aggregation type.

        Raises:
            ValueError:
                When the supplied value is not supported.
        """

        if isinstance(
            value,
            cls,
        ):
            return value

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "Analytics aggregation type must be an "
                "AnalyticsAggregationType instance or string."
            )

        normalized_value = value.strip().lower()

        if not normalized_value:
            raise ValueError(
                "Analytics aggregation type is required."
            )

        try:
            return cls(
                normalized_value
            )

        except ValueError as exc:
            raise ValueError(
                "Invalid Analytics aggregation type."
            ) from exc

    @property
    def code(
        self,
    ) -> str:
        """
        Return the canonical aggregation code.
        """

        return self.value

    @property
    def label(
        self,
    ) -> str:
        """
        Return the human-readable aggregation label.
        """

        labels = {
            self.COUNT: "Count",
            self.SUM: "Sum",
            self.AVERAGE: "Average",
            self.MINIMUM: "Minimum",
            self.MAXIMUM: "Maximum",
        }

        return labels[self]

    def to_dict(
        self,
    ) -> dict[str, str]:
        """
        Convert the aggregation type into a stable,
        provider-neutral dictionary representation.
        """

        return {
            "code": self.code,
            "label": self.label,
        }


@dataclass(frozen=True)
class AnalyticsMetric:
    """
    Represents a provider-neutral analytics metric definition.

    An analytics metric describes what should be measured,
    which source value is relevant, and which aggregation
    operation is requested.

    Metric execution, data-provider access, query generation,
    persistence, presentation, authorization, auditing,
    governance, and telemetry remain outside this contract.
    """

    code: str

    name: str

    aggregation: AnalyticsAggregationType

    source: str | None = None

    description: str | None = None

    unit: str | None = None

    category: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    active: bool = True

    def __post_init__(self) -> None:
        """
        Validate and normalize the analytics metric.
        """

        if not isinstance(
            self.code,
            str,
        ):
            raise ValueError(
                "Analytics metric code must be a string."
            )

        normalized_code = self.code.strip()

        if not normalized_code:
            raise ValueError(
                "Analytics metric code is required."
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
                "Analytics metric name must be a string."
            )

        normalized_name = self.name.strip()

        if not normalized_name:
            raise ValueError(
                "Analytics metric name is required."
            )

        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

        aggregation = self.aggregation

        if isinstance(
            aggregation,
            str,
        ):
            try:
                aggregation = (
                    AnalyticsAggregationType.normalize(
                        aggregation
                    )
                )

            except ValueError as exc:
                raise ValueError(
                    "Invalid analytics aggregation type."
                ) from exc

            object.__setattr__(
                self,
                "aggregation",
                aggregation,
            )

        elif not isinstance(
            aggregation,
            AnalyticsAggregationType,
        ):
            raise ValueError(
                "Analytics metric aggregation must be an "
                "AnalyticsAggregationType."
            )

        if self.source is not None:

            if not isinstance(
                self.source,
                str,
            ):
                raise ValueError(
                    "Analytics metric source must be a string "
                    "or None."
                )

            normalized_source = self.source.strip()

            if not normalized_source:
                object.__setattr__(
                    self,
                    "source",
                    None,
                )
            else:
                object.__setattr__(
                    self,
                    "source",
                    normalized_source,
                )

        if (
            self.aggregation
            is not AnalyticsAggregationType.COUNT
            and self.source is None
        ):
            raise ValueError(
                "Analytics metric source is required for "
                f"{self.aggregation.value} aggregation."
            )

        if self.description is not None:

            if not isinstance(
                self.description,
                str,
            ):
                raise ValueError(
                    "Analytics metric description must be a "
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

        if self.unit is not None:

            if not isinstance(
                self.unit,
                str,
            ):
                raise ValueError(
                    "Analytics metric unit must be a string "
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
                    "Analytics metric category must be a "
                    "string or None."
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
                "Analytics metric metadata must be a dictionary."
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
                "Analytics metric active flag must be a boolean."
            )

    @property
    def identifier(
        self,
    ) -> str:
        """
        Return the canonical analytics metric identifier.
        """

        return self.code.upper()

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the analytics metric into a stable,
        provider-neutral dictionary representation.
        """

        return {
            "code": self.code,
            "name": self.name,
            "aggregation": self.aggregation.value,
            "source": self.source,
            "description": self.description,
            "unit": self.unit,
            "category": self.category,
            "metadata": dict(
                self.metadata
            ),
            "active": self.active,
        }


__all__ = [
    "AnalyticsAggregationType",
    "AnalyticsMetric",
]
