"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report query contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReportQuery:
    """
    Represents a provider-neutral request for report data.

    The query contract identifies the report whose data is
    being requested and provides a framework-neutral metadata
    boundary for query context.

    Query execution, filtering, sorting, pagination,
    parameterization, persistence, and provider-specific
    interpretation remain outside this contract.
    """

    report_code: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

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

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
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

        return {
            "report_code": self.report_code,
            "metadata": dict(
                self.metadata
            ),
        }


__all__ = [
    "ReportQuery",
]
