"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report query contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.data import QueryOptions


@dataclass(frozen=True)
class ReportQuery:
    """
    Represents a provider-neutral request for report data.

    The query contract identifies the report whose data is
    being requested and provides framework-neutral metadata
    and enterprise query options.

    Query execution, provider-specific interpretation,
    authorization, governance, auditing, persistence,
    and transaction management remain outside this contract.
    """

    report_code: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    query_options: QueryOptions | None = None

    def __post_init__(self) -> None:
        """
        Validate and normalize the report query.
        """

        if not isinstance(
            self.report_code,
            str,
        ):
            raise ValueError(
                "Report query report_code must be a string."
            )

        normalized_code = (
            self.report_code.strip()
        )

        if not normalized_code:
            raise ValueError(
                "Report query report_code is required."
            )

        object.__setattr__(
            self,
            "report_code",
            normalized_code,
        )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report query metadata must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

        if (
            self.query_options is not None
            and not isinstance(
                self.query_options,
                QueryOptions,
            )
        ):
            raise ValueError(
                "Report query query_options must be "
                "a QueryOptions instance or None."
            )

    @property
    def identifier(self) -> str:
        """
        Return the canonical report query identifier.
        """

        return self.report_code.upper()

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the report query into a serializable
        dictionary representation.
        """

        result = {
        "report_code": self.report_code,
        "metadata": dict(
            self.metadata
        ),
    }

        if self.query_options is not None:
           result["query_options"] = (
               self.query_options.to_dict()
            )

        return result


__all__ = [
    "ReportQuery",
]
