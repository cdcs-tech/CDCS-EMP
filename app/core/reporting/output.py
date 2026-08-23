"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report output contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core.reporting.query_results import (
    ReportQueryResult,
)


class ReportOutputFormat(str, Enum):
    """
    Supported provider-neutral report output formats.

    The enum defines the output vocabulary only.
    Actual format generation belongs to the exporter
    abstraction introduced in later reporting stages.
    """

    JSON = "json"

    CSV = "csv"

    XLSX = "xlsx"

    PDF = "pdf"


@dataclass(frozen=True)
class ReportOutputRequest:
    """
    Represents a provider-neutral request to produce
    an output representation of an executed report.

    The request describes what output is required without
    prescribing how the output is generated.

    Output generation, exporter resolution, persistence,
    presentation, authorization, governance, auditing,
    and telemetry remain outside this contract.
    """

    result: ReportQueryResult

    format: ReportOutputFormat

    filename: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """
        Validate and normalize the output request.
        """

        if not isinstance(
            self.result,
            ReportQueryResult,
        ):
            raise ValueError(
                "Report output result must be a "
                "ReportQueryResult instance."
            )

        output_format = self.format

        if isinstance(
            output_format,
            str,
        ):
            try:
                output_format = ReportOutputFormat(
                    output_format.strip().lower()
                )
            except ValueError as exc:
                raise ValueError(
                    "Invalid report output format."
                ) from exc

            object.__setattr__(
                self,
                "format",
                output_format,
            )

        elif not isinstance(
            output_format,
            ReportOutputFormat,
        ):
            raise ValueError(
                "Report output format must be a "
                "ReportOutputFormat."
            )

        if self.filename is not None:

            if not isinstance(
                self.filename,
                str,
            ):
                raise ValueError(
                    "Report output filename must be a string "
                    "or None."
                )

            normalized_filename = (
                self.filename.strip()
            )

            if not normalized_filename:
                raise ValueError(
                    "Report output filename cannot be empty."
                )

            object.__setattr__(
                self,
                "filename",
                normalized_filename,
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise ValueError(
                "Report output metadata must be a dictionary."
            )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    @property
    def report_code(self) -> str:
        """
        Return the report code associated with the
        output request.
        """

        return self.result.query.report_code

    @property
    def identifier(self) -> str:
        """
        Return the canonical report identifier associated
        with the output request.
        """

        return self.result.query.identifier

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert the output request into a serializable
        dictionary representation.
        """

        return {
            "result": self.result.to_dict(),
            "format": self.format.value,
            "filename": self.filename,
            "metadata": dict(
                self.metadata
            ),
        }


__all__ = [
    "ReportOutputFormat",
    "ReportOutputRequest",
]
