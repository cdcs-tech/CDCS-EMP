"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report result contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core.reporting.models import (
    ReportDefinition,
)


class ReportResultStatus(str, Enum):
    """
    Supported report result states.
    """

    SUCCESS = "success"

    EMPTY = "empty"

    FAILED = "failed"


@dataclass
class ReportResult:
    """
    Standard result produced by a report provider.

    The result contract provides a provider-neutral
    representation of report output.

    Presentation, persistence, authorization,
    governance, auditing, and telemetry remain
    outside this contract.
    """

    definition: ReportDefinition

    data: Any = None

    status: ReportResultStatus = (
        ReportResultStatus.SUCCESS
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    message: str | None = None

    error: str | None = None

    @property
    def is_success(self) -> bool:
        """
        Determine whether the result represents
        successful report generation.
        """

        return (
            self.status
            == ReportResultStatus.SUCCESS
        )

    @property
    def is_empty(self) -> bool:
        """
        Determine whether the result contains
        no report data.
        """

        return (
            self.status
            == ReportResultStatus.EMPTY
        )

    @property
    def is_failed(self) -> bool:
        """
        Determine whether report generation failed.
        """

        return (
            self.status
            == ReportResultStatus.FAILED
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the result into a serializable
        dictionary representation.
        """

        return {
            "definition": (
                self.definition.to_dict()
            ),
            "data": self.data,
            "status": self.status.value,
            "metadata": dict(
                self.metadata
            ),
            "message": self.message,
            "error": self.error,
        }


__all__ = [
    "ReportResultStatus",
    "ReportResult",
]
