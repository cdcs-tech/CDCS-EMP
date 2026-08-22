"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report execution context contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReportExecutionContext:
    """
    Represents execution-level context associated with
    a report execution request.

    The execution context provides framework-neutral
    information accompanying report execution without
    coupling the reporting framework to authorization,
    governance, auditing, persistence, transaction
    management, or presentation concerns.

    Query-specific information belongs to ReportQuery.
    Execution input values belong to ReportExecutionRequest.
    """

    correlation_id: str | None = None

    requested_by: str | None = None

    source: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the execution context.
        """

        if self.correlation_id is not None:

            if not isinstance(
                self.correlation_id,
                str,
            ):
                raise ValueError(
                    "Report execution correlation_id "
                    "must be a string or None."
                )

            normalized_correlation_id = (
                self.correlation_id.strip()
            )

            if not normalized_correlation_id:
                raise ValueError(
                    "Report execution correlation_id "
                    "cannot be empty."
                )

            object.__setattr__(
                self,
                "correlation_id",
                normalized_correlation_id,
            )

        if self.requested_by is not None:

            if not isinstance(
                self.requested_by,
                str,
            ):
                raise ValueError(
                    "Report execution requested_by "
                    "must be a string or None."
                )

            normalized_requested_by = (
                self.requested_by.strip()
            )

            if not normalized_requested_by:
                raise ValueError(
                    "Report execution requested_by "
                    "cannot be empty."
                )

            object.__setattr__(
                self,
                "requested_by",
                normalized_requested_by,
            )

        if self.source is not None:

            if not isinstance(
                self.source,
                str,
            ):
                raise ValueError(
                    "Report execution source "
                    "must be a string or None."
                )

            normalized_source = (
                self.source.strip()
            )

            if not normalized_source:
                raise ValueError(
                    "Report execution source "
                    "cannot be empty."
                )

            object.__setattr__(
                self,
                "source",
                normalized_source,
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report execution metadata "
                "must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the execution context into a
        serializable dictionary representation.
        """

        return {
            "correlation_id": self.correlation_id,
            "requested_by": self.requested_by,
            "source": self.source,
            "metadata": dict(
                self.metadata
            ),
        }


__all__ = [
    "ReportExecutionContext",
]
