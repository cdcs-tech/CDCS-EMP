"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report query execution contracts and default execution
implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.data import QueryOptions

from app.core.reporting.data_providers import (
    ReportDataProvider,
)
from app.core.reporting.queries import (
    ReportQuery,
)
from app.core.reporting.query_results import (
    ReportQueryResult,
    ReportQueryResultStatus,
)


class ReportQueryExecutor(ABC):
    """
    Abstract contract for executing report queries.

    A query executor is responsible for executing a
    provider-neutral report query through a supplied
    data provider and returning a standardized query
    result.

    Provider resolution, authorization, governance,
    auditing, telemetry, persistence, and presentation
    remain outside this contract.
    """

    @abstractmethod
    def execute(
        self,
        provider: ReportDataProvider,
        query: ReportQuery,
        options: QueryOptions | None = None,
    ) -> ReportQueryResult:
        """
        Execute a report query through a data provider.

        Args:
            provider:
                Data provider responsible for obtaining
                the report data.

            query:
                Provider-neutral report query.

            options:
                Optional Enterprise Data Framework query
                options passed through to the provider.

        Returns:
            Standardized report query result.
        """

        raise NotImplementedError


class DefaultReportQueryExecutor(
    ReportQueryExecutor,
):
    """
    Default implementation of report query execution.

    The executor coordinates the execution boundary between
    a ReportQuery and a ReportDataProvider.

    Responsibilities are deliberately limited to:

    - validating execution inputs
    - invoking the supplied provider
    - passing QueryOptions through unchanged
    - normalizing provider output into ReportQueryResult
    - identifying empty provider results
    - preserving provider and execution metadata
    - converting provider execution failures into a
      standardized failed query result

    Provider discovery, authorization, governance,
    auditing, telemetry, persistence, and presentation
    remain outside this implementation.
    """

    def execute(
        self,
        provider: ReportDataProvider,
        query: ReportQuery,
        options: QueryOptions | None = None,
    ) -> ReportQueryResult:
        """
        Execute a report query through the supplied provider.

        Args:
            provider:
                Data provider responsible for obtaining
                the report data.

            query:
                Provider-neutral report query.

            options:
                Optional Enterprise Data Framework query
                options.

        Returns:
            Standardized ReportQueryResult.

        Raises:
            ValueError:
                When the provider, query, or query options
                are invalid.
        """

        self._validate_provider(
            provider
        )

        self._validate_query(
            query
        )

        self._validate_options(
            options
        )

        try:

            data = provider.execute(
                query,
                options,
            )

        except Exception as exc:

            return ReportQueryResult(
                query=query,
                data=None,
                status=(
                    ReportQueryResultStatus.FAILED
                ),
                metadata=self._build_metadata(
                    provider=provider,
                    options=options,
                ),
                message="Report query execution failed.",
                error=str(exc),
            )

        status = self._resolve_status(
            data
        )

        message = self._resolve_message(
            status
        )

        return ReportQueryResult(
            query=query,
            data=data,
            status=status,
            metadata=self._build_metadata(
                provider=provider,
                options=options,
            ),
            message=message,
        )

    def _validate_provider(
        self,
        provider: ReportDataProvider,
    ) -> None:
        """
        Validate the supplied report data provider.
        """

        if not isinstance(
            provider,
            ReportDataProvider,
        ):
            raise ValueError(
                "Report data provider must implement "
                "ReportDataProvider."
            )

    def _validate_query(
        self,
        query: ReportQuery,
    ) -> None:
        """
        Validate the supplied report query.
        """

        if not isinstance(
            query,
            ReportQuery,
        ):
            raise ValueError(
                "Report query must be a ReportQuery."
            )

    def _validate_options(
        self,
        options: QueryOptions | None,
    ) -> None:
        """
        Validate optional Enterprise Data Framework
        query options.
        """

        if (
            options is not None
            and not isinstance(
                options,
                QueryOptions,
            )
        ):
            raise ValueError(
                "Query options must be a QueryOptions "
                "instance or None."
            )

    def _resolve_status(
        self,
        data: Any,
    ) -> ReportQueryResultStatus:
        """
        Determine the standardized result status.

        None and empty collection-like results are
        represented as EMPTY.

        Other provider results are represented as
        SUCCESS.
        """

        if data is None:

            return (
                ReportQueryResultStatus.EMPTY
            )

        if isinstance(
            data,
            (list, tuple, set, frozenset),
        ) and not data:

            return (
                ReportQueryResultStatus.EMPTY
            )

        return (
            ReportQueryResultStatus.SUCCESS
        )

    def _resolve_message(
        self,
        status: ReportQueryResultStatus,
    ) -> str | None:
        """
        Provide a standardized execution message.
        """

        if status == ReportQueryResultStatus.EMPTY:

            return (
                "Report query executed successfully "
                "but returned no data."
            )

        return None

    def _build_metadata(
        self,
        provider: ReportDataProvider,
        options: QueryOptions | None,
    ) -> dict[str, Any]:
        """
        Build standardized execution metadata.

        Provider metadata is intentionally limited to
        execution context. Query-specific metadata remains
        part of ReportQuery.
        """

        metadata: dict[str, Any] = {
            "provider": provider.name,
        }

        if options is not None:

            metadata[
                "query_options"
            ] = options.to_dict()

        return metadata


__all__ = [
    "ReportQueryExecutor",
    "DefaultReportQueryExecutor",
]
