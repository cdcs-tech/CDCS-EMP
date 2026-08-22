"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report query result contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core.reporting.queries import (
    ReportQuery,
)


class ReportQueryResultStatus(str, Enum):
    """
    Supported report query result states.
    """

    SUCCESS = "success"

    EMPTY = "empty"

    FAILED = "failed"


@dataclass
class ReportQueryResult:
    """
    Standard result produced by report query execution.

    The result contract provides a provider-neutral
    representation of data returned from a report query.

    Report generation, presentation, persistence,
    authorization, governance, auditing, and telemetry
    remain outside this contract.
    """

    query: ReportQuery

    data: Any = None

    status: ReportQueryResultStatus = (
        ReportQueryResultStatus.SUCCESS
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    message: str | None = None

    error: str | None = None

    @property
    def is_success(self) -> bool:
        """
        Determine whether the query result represents
        successful query execution.
        """

        return (
            self.status
            == ReportQueryResultStatus.SUCCESS
        )

    @property
    def is_empty(self) -> bool:
        """
        Determine whether the query result contains
        no query data.
        """

        return (
            self.status
            == ReportQueryResultStatus.EMPTY
        )

    @property
    def is_failed(self) -> bool:
        """
        Determine whether query execution failed.
        """

        return (
            self.status
            == ReportQueryResultStatus.FAILED
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the query result into a serializable
        dictionary representation.
        """

        return {
            "query": self.query.to_dict(),
            "data": self.data,
            "status": self.status.value,
            "metadata": dict(
                self.metadata
            ),
            "message": self.message,
            "error": self.error,
        }


__all__ = [
    "ReportQueryResultStatus",
    "ReportQueryResult",
]
