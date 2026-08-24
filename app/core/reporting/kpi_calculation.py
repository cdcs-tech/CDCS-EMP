"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Provider-neutral KPI calculation contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core.reporting.analytics import (
    ReportKPI,
)


class ReportKPICalculationStatus(str, Enum):
    """
    Supported KPI calculation result states.
    """

    SUCCESS = "success"

    EMPTY = "empty"

    FAILED = "failed"


@dataclass(frozen=True)
class ReportKPICalculationRequest:
    """
    Represents a provider-neutral request to calculate
    a report KPI.

    The request identifies the KPI to be calculated and
    provides optional calculation input, parameters,
    and metadata.

    KPI calculation logic, aggregation, query execution,
    persistence, presentation, authorization, governance,
    auditing, telemetry, and scheduling remain outside
    this contract.
    """

    kpi: ReportKPI

    data: Any = None

    parameters: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the KPI calculation request.
        """

        if not isinstance(
            self.kpi,
            ReportKPI,
        ):
            raise ValueError(
                "KPI calculation request kpi must be "
                "a ReportKPI instance."
            )

        if not isinstance(
            self.parameters,
            dict,
        ):
            raise ValueError(
                "KPI calculation request parameters "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "parameters",
            dict(self.parameters),
        )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "KPI calculation request metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    @property
    def kpi_code(self) -> str:
        """
        Return the KPI code associated with the
        calculation request.
        """

        return self.kpi.code

    @property
    def identifier(self) -> str:
        """
        Return the canonical KPI identifier associated
        with the calculation request.
        """

        return self.kpi.identifier

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the calculation request into a stable,
        provider-neutral dictionary representation.
        """

        return {
            "kpi": self.kpi.to_dict(),
            "data": self.data,
            "parameters": dict(
                self.parameters
            ),
            "metadata": dict(
                self.metadata
            ),
        }


@dataclass
class ReportKPICalculationResult:
    """
    Standard result produced by KPI calculation.

    The result provides a provider-neutral representation
    of a calculated KPI value.

    Calculation execution, aggregation, persistence,
    presentation, authorization, governance, auditing,
    telemetry, and scheduling remain outside this contract.
    """

    kpi: ReportKPI

    value: Any = None

    status: ReportKPICalculationStatus = (
        ReportKPICalculationStatus.SUCCESS
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    message: str | None = None

    error: str | None = None

    def __post_init__(self) -> None:
        """
        Validate the KPI calculation result.
        """

        if not isinstance(
            self.kpi,
            ReportKPI,
        ):
            raise ValueError(
                "KPI calculation result kpi must be "
                "a ReportKPI instance."
            )

        status = self.status

        if isinstance(
            status,
            str,
        ):
            try:
                status = ReportKPICalculationStatus(
                    status.strip().lower()
                )
            except ValueError as exc:
                raise ValueError(
                    "Invalid KPI calculation status."
                ) from exc

            self.status = status

        elif not isinstance(
            status,
            ReportKPICalculationStatus,
        ):
            raise ValueError(
                "KPI calculation result status must be "
                "a ReportKPICalculationStatus."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "KPI calculation result metadata "
                "must be a dictionary."
            )

        self.metadata = dict(
            self.metadata
        )

    @property
    def kpi_code(self) -> str:
        """
        Return the KPI code associated with the
        calculation result.
        """

        return self.kpi.code

    @property
    def identifier(self) -> str:
        """
        Return the canonical KPI identifier associated
        with the calculation result.
        """

        return self.kpi.identifier

    @property
    def is_success(self) -> bool:
        """
        Determine whether the calculation succeeded.
        """

        return (
            self.status
            == ReportKPICalculationStatus.SUCCESS
        )

    @property
    def is_empty(self) -> bool:
        """
        Determine whether the calculation produced
        no KPI value.
        """

        return (
            self.status
            == ReportKPICalculationStatus.EMPTY
        )

    @property
    def is_failed(self) -> bool:
        """
        Determine whether KPI calculation failed.
        """

        return (
            self.status
            == ReportKPICalculationStatus.FAILED
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the calculation result into a stable,
        provider-neutral dictionary representation.
        """

        return {
            "kpi": self.kpi.to_dict(),
            "value": self.value,
            "status": self.status.value,
            "metadata": dict(
                self.metadata
            ),
            "message": self.message,
            "error": self.error,
        }


__all__ = [
    "ReportKPICalculationStatus",
    "ReportKPICalculationRequest",
    "ReportKPICalculationResult",
]
