"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Provider-neutral report export format contract.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ReportExportFormat(str, Enum):
    """
    Supported report export format identities.

    This contract identifies the desired export representation
    without coupling the reporting framework to any concrete
    exporter implementation or external export library.

    Exporter discovery, exporter implementation, output
    generation, storage, transport, authorization, auditing,
    and governance remain outside this contract.
    """

    CSV = "csv"

    XLSX = "xlsx"

    PDF = "pdf"

    JSON = "json"

    @classmethod
    def normalize(
        cls,
        value: ReportExportFormat | str,
    ) -> ReportExportFormat:
        """
        Normalize an export format value into a
        ReportExportFormat instance.

        Args:
            value:
                A ReportExportFormat instance or string value.

        Returns:
            ReportExportFormat:
                The normalized export format.

        Raises:
            ValueError:
                When the supplied value is not a supported
                report export format.
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
                "Report export format must be a "
                "ReportExportFormat instance or string."
            )

        normalized_value = value.strip().lower()

        if not normalized_value:
            raise ValueError(
                "Report export format is required."
            )

        try:
            return cls(
                normalized_value
            )

        except ValueError as exc:

            raise ValueError(
                "Report export format "
                f"'{normalized_value}' is not supported."
            ) from exc

    @property
    def code(
        self,
    ) -> str:
        """
        Return the canonical format code.

        The code is suitable for configuration,
        metadata, API contracts, and persistence.
        """

        return self.value

    @property
    def label(
        self,
    ) -> str:
        """
        Return the human-readable format label.
        """

        labels = {
            self.CSV: "CSV",
            self.XLSX: "Excel",
            self.PDF: "PDF",
            self.JSON: "JSON",
        }

        return labels[self]

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize the export format into a stable
        provider-neutral dictionary representation.
        """

        return {
            "code": self.code,
            "label": self.label,
        }


__all__ = [
    "ReportExportFormat",
]
