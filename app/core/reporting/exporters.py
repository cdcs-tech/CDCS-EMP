"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Provider-neutral report exporter contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.reporting.export_formats import (
    ReportExportFormat,
)
from app.core.reporting.output import (
    ReportOutputRequest,
)


class ReportExporter(ABC):
    """
    Abstract provider-neutral contract for report exporters.

    A report exporter transforms a ReportOutputRequest into
    an export representation identified by a supported
    ReportExportFormat.

    The contract defines exporter identity, format capability,
    and export execution only.

    Concrete export generation, external libraries, file
    storage, transport, authorization, auditing, governance,
    telemetry, and exporter discovery remain outside this
    contract.
    """

    @property
    @abstractmethod
    def name(
        self,
    ) -> str:
        """
        Return the canonical exporter name.

        The name identifies the exporter implementation
        independently of its output format.
        """

        raise NotImplementedError

    @property
    @abstractmethod
    def format(
        self,
    ) -> ReportExportFormat:
        """
        Return the export format supported by this exporter.
        """

        raise NotImplementedError

    def supports(
        self,
        export_format: ReportExportFormat | str,
    ) -> bool:
        """
        Determine whether this exporter supports the
        supplied export format.

        String values are normalized through the
        ReportExportFormat contract.

        Args:
            export_format:
                A ReportExportFormat instance or supported
                string representation.

        Returns:
            bool:
                True when the exporter supports the supplied
                format; otherwise False.

        Raises:
            ValueError:
                When the supplied export format is invalid.
        """

        normalized_format = (
            ReportExportFormat.normalize(
                export_format
            )
        )

        return normalized_format is self.format

    @abstractmethod
    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        """
        Export the supplied report output request.

        Concrete exporters are responsible for transforming
        the provider-neutral output request into their
        concrete export representation.

        Args:
            request:
                Provider-neutral report output request.

        Returns:
            Any:
                Concrete exporter output.

        Raises:
            NotImplementedError:
                When a concrete exporter has not implemented
                the export operation.
        """

        raise NotImplementedError


__all__ = [
    "ReportExporter",
]
