"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report export execution service.
"""

from __future__ import annotations

from typing import Any

from app.core.reporting.authorization import (
    ReportAuthorizationRequest,
)
from app.core.reporting.authorization_adapter import (
    ReportingAuthorizationAdapter,
)
from app.core.reporting.exceptions import (
    ReportExecutionException,
)
from app.core.reporting.export_formats import (
    ReportExportFormat,
)
from app.core.reporting.exporter_registry import (
    ReportExporterRegistry,
)
from app.core.reporting.output import (
    ReportOutputRequest,
)


class ReportExportExecutionService:
    """
    Application-level service responsible for orchestrating
    provider-neutral report export execution.

    The service coordinates:

    - output request validation,
    - optional export authorization,
    - output-format normalization,
    - exporter resolution,
    - exporter invocation, and
    - export execution failure translation.

    Concrete export generation, file storage, transport,
    presentation, governance, auditing, telemetry, and
    persistence remain outside this service.
    """

    def __init__(
        self,
        exporter_registry: ReportExporterRegistry,
        authorization_adapter: ReportingAuthorizationAdapter | None = None,
    ) -> None:
        """
        Initialize the report export execution service.

        Args:
            exporter_registry:
                Registry responsible for resolving exporters.

            authorization_adapter:
                Optional reporting authorization adapter used
                when an authorization request is supplied.

        Raises:
            ValueError:
                When an invalid exporter registry or
                authorization adapter is supplied.
        """

        if not isinstance(
            exporter_registry,
            ReportExporterRegistry,
        ):
            raise ValueError(
                "A ReportExporterRegistry is required."
            )

        if (
            authorization_adapter is not None
            and not isinstance(
                authorization_adapter,
                ReportingAuthorizationAdapter,
            )
        ):
            raise ValueError(
                "A ReportingAuthorizationAdapter is required."
            )

        self.exporter_registry = (
            exporter_registry
        )

        self.authorization_adapter = (
            authorization_adapter
        )

    def execute(
        self,
        request: ReportOutputRequest,
        *,
        authorization_request: ReportAuthorizationRequest | None = None,
    ) -> Any:
        """
        Execute a report export request.

        The service validates the request, optionally evaluates
        export authorization, resolves the appropriate exporter,
        delegates export execution, and returns the exporter
        output unchanged.

        Exceptions raised during exporter resolution or
        execution are translated into the reporting
        execution exception boundary.
        """

        self._validate_request(
            request
        )

        self._authorize(
            authorization_request
        )

        try:

            export_format = (
                self._resolve_export_format(
                    request
                )
            )

            exporter = (
                self.exporter_registry.resolve(
                    export_format
                )
            )

            return exporter.export(
                request
            )

        except ReportExecutionException:
            raise

        except Exception as exc:

            raise ReportExecutionException(
                "Report export execution failed."
            ) from exc

    def _validate_request(
        self,
        request: ReportOutputRequest,
    ) -> None:
        """
        Validate the export execution request.
        """

        if not isinstance(
            request,
            ReportOutputRequest,
        ):
            raise ValueError(
                "Report output request must be a "
                "ReportOutputRequest instance."
            )

    def _authorize(
        self,
        authorization_request: ReportAuthorizationRequest | None,
    ) -> None:
        """
        Evaluate export authorization when an authorization
        request is supplied.
        """

        if authorization_request is None:
            return

        if self.authorization_adapter is None:
            raise ReportExecutionException(
                "Report export authorization adapter is required."
            )

        if authorization_request.operation.value != "export":
            raise ReportExecutionException(
                "Report export authorization requires the "
                "export operation."
            )

        try:

            decision = self.authorization_adapter.authorize(
                authorization_request
            )

        except Exception as exc:

            raise ReportExecutionException(
                "Report export authorization failed."
            ) from exc

        if not decision.is_allowed:
            raise ReportExecutionException(
                decision.reason
                or "Report export authorization denied."
            )

    def _resolve_export_format(
        self,
        request: ReportOutputRequest,
    ) -> ReportExportFormat:
        """
        Translate the output-format contract into the
        exporter-format contract.

        ReportOutputFormat and ReportExportFormat intentionally
        remain separate contracts. This service owns their
        execution-boundary translation.
        """

        try:

            return ReportExportFormat.normalize(
                request.format.value
            )

        except ValueError as exc:

            raise ReportExecutionException(
                "Report output format cannot be resolved "
                "for export execution."
            ) from exc


__all__ = [
    "ReportExportExecutionService",
]
