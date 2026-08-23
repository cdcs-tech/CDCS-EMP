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
from app.core.reporting.execution_context import (
    ReportExecutionContext,
)
from app.core.reporting.filters import (
    ReportFilterCollection,
)
from app.core.reporting.queries import (
    ReportQuery,
)
from app.core.reporting.query_results import (
    ReportQueryResult,
    ReportQueryResultStatus,
)
from app.core.reporting.sorting import (
    ReportSortCollection,
)


class ReportQueryExecutor(ABC):
    """
    Abstract contract for executing report queries.

    A query executor is responsible for executing a
    provider-neutral report query through a supplied
    data provider and returning a standardized query
    result.

    Report execution parameters, context, query options,
    filters, and sorting are passed explicitly so that
    the execution boundary does not lose request-level
    information.

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
        parameters: dict[str, Any] | None = None,
        context: ReportExecutionContext | None = None,
        filters: ReportFilterCollection | None = None,
        sorting: ReportSortCollection | None = None,
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
                options.

            parameters:
                Optional report-specific execution parameters.

            context:
                Optional report execution context.

            filters:
                Provider-neutral report filters.

            sorting:
                Provider-neutral report sorting.

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
    - preserving report execution parameters
    - preserving report execution context
    - preserving provider-neutral filters
    - preserving provider-neutral sorting
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
        parameters: dict[str, Any] | None = None,
        context: ReportExecutionContext | None = None,
        filters: ReportFilterCollection | None = None,
        sorting: ReportSortCollection | None = None,
    ) -> ReportQueryResult:
        """
        Execute a report query through the supplied provider.
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

        self._validate_parameters(
            parameters
        )

        self._validate_context(
            context
        )

        self._validate_filters(
            filters
        )

        self._validate_sorting(
            sorting
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
                    parameters=parameters,
                    context=context,
                    filters=filters,
                    sorting=sorting,
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
                parameters=parameters,
                context=context,
                filters=filters,
                sorting=sorting,
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

    def _validate_parameters(
        self,
        parameters: dict[str, Any] | None,
    ) -> None:
        """
        Validate optional report execution parameters.
        """

        if (
            parameters is not None
            and not isinstance(
                parameters,
                dict,
            )
        ):
            raise ValueError(
                "Report execution parameters must be "
                "a dictionary or None."
            )

    def _validate_context(
        self,
        context: ReportExecutionContext | None,
    ) -> None:
        """
        Validate optional report execution context.
        """

        if (
            context is not None
            and not isinstance(
                context,
                ReportExecutionContext,
            )
        ):
            raise ValueError(
                "Report execution context must be a "
                "ReportExecutionContext instance or None."
            )

    def _validate_filters(
        self,
        filters: ReportFilterCollection | None,
    ) -> None:
        """
        Validate optional provider-neutral report filters.
        """

        if (
            filters is not None
            and not isinstance(
                filters,
                ReportFilterCollection,
            )
        ):
            raise ValueError(
                "Report execution filters must be a "
                "ReportFilterCollection instance or None."
            )

    def _validate_sorting(
        self,
        sorting: ReportSortCollection | None,
    ) -> None:
        """
        Validate optional provider-neutral report sorting.
        """

        if (
            sorting is not None
            and not isinstance(
                sorting,
                ReportSortCollection,
            )
        ):
            raise ValueError(
                "Report execution sorting must be a "
                "ReportSortCollection instance or None."
            )

    def _resolve_status(
        self,
        data: Any,
    ) -> ReportQueryResultStatus:
        """
        Determine the standardized result status.
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
        parameters: dict[str, Any] | None,
        context: ReportExecutionContext | None,
        filters: ReportFilterCollection | None,
        sorting: ReportSortCollection | None,
    ) -> dict[str, Any]:
        """
        Build standardized execution metadata.

        Provider metadata is intentionally limited to
        execution information. Query-specific metadata
        remains part of ReportQuery.
        """

        metadata: dict[str, Any] = {
            "provider": provider.name,
        }

        if options is not None:

            metadata[
                "query_options"
            ] = options.to_dict()

        if parameters is not None:

            metadata[
                "parameters"
            ] = dict(parameters)

        if context is not None:

            metadata[
                "context"
            ] = context.to_dict()

        if filters is not None:

            metadata[
                "filters"
            ] = filters.to_list()

        if sorting is not None:

            metadata[
                "sorting"
            ] = sorting.to_list()

        return metadata


__all__ = [
    "ReportQueryExecutor",
    "DefaultReportQueryExecutor",
]
