"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report execution request contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.data import QueryOptions

from app.core.reporting.execution_context import (
    ReportExecutionContext,
)
from app.core.reporting.queries import (
    ReportQuery,
)


@dataclass(frozen=True)
class ReportExecutionRequest:
    """
    Represents a complete provider-neutral request
    to execute a report query.

    The execution request combines:

    - the report query,
    - report execution parameters,
    - execution-level context, and
    - optional enterprise data query options.

    The request does not perform provider resolution,
    query execution, authorization, governance, auditing,
    persistence, transaction management, or presentation.
    """

    query: ReportQuery

    parameters: dict[str, Any] = field(
        default_factory=dict
    )

    context: ReportExecutionContext = field(
        default_factory=ReportExecutionContext
    )

    query_options: QueryOptions | None = None

    def __post_init__(self) -> None:
        """
        Validate and normalize the execution request.
        """

        if not isinstance(
            self.query,
            ReportQuery,
        ):
            raise ValueError(
                "Report execution query must be "
                "a ReportQuery instance."
            )

        if not isinstance(
            self.parameters,
            dict,
        ):
            raise ValueError(
                "Report execution parameters "
                "must be a dictionary."
            )

        if not isinstance(
            self.context,
            ReportExecutionContext,
        ):
            raise ValueError(
                "Report execution context must be "
                "a ReportExecutionContext instance."
            )

        if (
            self.query_options is not None
            and not isinstance(
                self.query_options,
                QueryOptions,
            )
        ):
            raise ValueError(
                "Report execution query_options must be "
                "a QueryOptions instance or None."
            )

        object.__setattr__(
            self,
            "parameters",
            dict(self.parameters),
        )

    @property
    def report_code(self) -> str:
        """
        Return the report code associated with the
        execution request.
        """

        return self.query.report_code

    @property
    def identifier(self) -> str:
        """
        Return the canonical report identifier.
        """

        return self.query.identifier

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the execution request into a
        serializable dictionary representation.
        """

        return {
            "query": self.query.to_dict(),
            "parameters": dict(
                self.parameters
            ),
            "context": self.context.to_dict(),
            "query_options": (
                self.query_options.to_dict()
                if self.query_options is not None
                else None
            ),
        }


__all__ = [
    "ReportExecutionRequest",
]
