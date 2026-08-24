"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report exporter registration and resolution.
"""

from __future__ import annotations

from typing import Iterable

from app.core.reporting.exceptions import (
    ReportRegistrationException,
)
from app.core.reporting.export_formats import (
    ReportExportFormat,
)
from app.core.reporting.exporters import (
    ReportExporter,
)


class ReportExporterRegistry:
    """
    Registry responsible for registering and resolving
    report exporters.

    The registry owns exporter discovery and selection only.

    Export execution, output generation, storage, transport,
    authorization, auditing, governance, telemetry,
    and presentation remain outside this contract.
    """

    def __init__(
        self,
        exporters: Iterable[
            ReportExporter
        ] | None = None,
    ) -> None:
        """
        Initialize the exporter registry.

        Args:
            exporters:
                Optional initial exporter collection.

        Raises:
            ReportRegistrationException:
                When an invalid exporter is supplied.
        """

        self._exporters: dict[
            ReportExportFormat,
            ReportExporter,
        ] = {}

        if exporters is not None:

            for exporter in exporters:

                self.register(
                    exporter
                )

    def register(
        self,
        exporter: ReportExporter,
    ) -> None:
        """
        Register a report exporter.

        The export format is used as the canonical registry
        key.

        Raises:
            ReportRegistrationException:
                When the exporter is invalid or an exporter
                for the same format is already registered.
        """

        if not isinstance(
            exporter,
            ReportExporter,
        ):
            raise ReportRegistrationException(
                "Exporter must implement "
                "ReportExporter."
            )

        export_format = (
            self._normalize_format(
                exporter.format
            )
        )

        if export_format in self._exporters:

            raise ReportRegistrationException(
                "Report exporter for format "
                f"'{export_format.value}' is already "
                "registered."
            )

        self._exporters[
            export_format
        ] = exporter

    def unregister(
        self,
        export_format: ReportExportFormat | str,
    ) -> None:
        """
        Remove a registered exporter.

        Raises:
            KeyError:
                When no exporter is registered for the
                supplied format.
            ValueError:
                When the supplied format is invalid.
        """

        normalized_format = (
            self._normalize_format(
                export_format
            )
        )

        del self._exporters[
            normalized_format
        ]

    def get(
        self,
        export_format: ReportExportFormat | str,
    ) -> ReportExporter:
        """
        Retrieve a registered exporter by format.

        Raises:
            KeyError:
                When no exporter is registered for the
                supplied format.
            ValueError:
                When the supplied format is invalid.
        """

        normalized_format = (
            self._normalize_format(
                export_format
            )
        )

        return self._exporters[
            normalized_format
        ]

    def has(
        self,
        export_format: ReportExportFormat | str,
    ) -> bool:
        """
        Determine whether an exporter is registered for
        the supplied format.

        Raises:
            ValueError:
                When the supplied format is invalid.
        """

        normalized_format = (
            self._normalize_format(
                export_format
            )
        )

        return (
            normalized_format
            in self._exporters
        )

    def all(
        self,
    ) -> tuple[
        ReportExporter,
        ...,
    ]:
        """
        Return all registered exporters.

        Registration order is preserved.
        """

        return tuple(
            self._exporters.values()
        )

    def resolve(
        self,
        export_format: ReportExportFormat | str,
    ) -> ReportExporter:
        """
        Resolve the exporter registered for the
        supplied export format.

        Raises:
            KeyError:
                When no exporter is registered for the
                supplied format.
            ValueError:
                When the supplied format is invalid.
        """

        normalized_format = (
            self._normalize_format(
                export_format
            )
        )

        return self._exporters[
            normalized_format
        ]

    @staticmethod
    def _normalize_format(
        export_format: ReportExportFormat | str,
    ) -> ReportExportFormat:
        """
        Normalize an export format through the canonical
        ReportExportFormat contract.
        """

        try:

            return ReportExportFormat.normalize(
                export_format
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid report export format."
            ) from exc


__all__ = [
    "ReportExporterRegistry",
]
