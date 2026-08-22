"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report execution service contract.
"""

from __future__ import annotations

from typing import Any

from app.core.reporting.exceptions import (
    ReportExecutionException,
)
from app.core.reporting.execution import (
    ReportQueryExecutor,
)
from app.core.reporting.execution_context import (
    ReportExecutionContext,
)
from app.core.reporting.execution_request import (
    ReportExecutionRequest,
)
from app.core.reporting.provider_registry import (
    ReportDataProviderRegistry,
)
from app.core.reporting.query_results import (
    ReportQueryResult,
)


class ReportExecutionService:
    """
    Application-level service responsible for orchestrating
    provider-neutral report execution.

    The service coordinates:

    - execution-request validation
    - provider resolution
    - execution-option propagation
    - execution-parameter propagation
    - execution-context propagation
    - query execution
    - standardized execution-result validation
    - execution failure translation

    The service preserves ReportQueryResult outcomes produced
    by the query executor, including SUCCESS, EMPTY, and
    FAILED results.

    Authorization, governance, auditing, telemetry,
    transaction management, persistence, and presentation
    remain outside this service.
    """

    def __init__(
        self,
        provider_registry: ReportDataProviderRegistry,
        query_executor: ReportQueryExecutor,
    ) -> None:
        """
        Initialize the report execution service.

        Args:
            provider_registry:
                Registry responsible for resolving a suitable
                report data provider.

            query_executor:
                Executor responsible for executing a query
                through the resolved provider.

        Raises:
            ValueError:
                When either dependency is missing or invalid.
        """

        if not isinstance(
            provider_registry,
            ReportDataProviderRegistry,
        ):
            raise ValueError(
                "A ReportDataProviderRegistry is required."
            )

        if not isinstance(
            query_executor,
            ReportQueryExecutor,
        ):
            raise ValueError(
                "A ReportQueryExecutor is required."
            )

        self.provider_registry = (
            provider_registry
        )

        self.query_executor = (
            query_executor
        )

    def execute(
        self,
        request: ReportExecutionRequest,
    ) -> ReportQueryResult:
        """
        Execute a provider-neutral report execution request.

        The service:

        1. validates the execution request,
        2. resolves the appropriate data provider,
        3. delegates execution to the query executor,
        4. validates the returned execution result, and
        5. returns the standardized ReportQueryResult.

        SUCCESS, EMPTY, and FAILED query results are valid
        execution outcomes and are returned unchanged.

        Exceptions raised during provider resolution or
        query execution are translated into the reporting
        execution exception boundary.

        Args:
            request:
                Complete provider-neutral report execution
                request.

        Returns:
            Standardized report query result.

        Raises:
            ValueError:
                When the supplied request is invalid.

            ReportExecutionException:
                When provider resolution or query execution
                raises an exception, or when the executor
                returns an invalid result.
        """

        self._validate_request(
            request
        )

        query = request.query

        parameters = dict(
            request.parameters
        )

        context = request.context

        try:

            provider = (
                self.provider_registry.resolve(
                    query
                )
            )

            result = self._execute_query(
                provider=provider,
                query=query,
                parameters=parameters,
                context=context,
            )

        except Exception as exc:

            if isinstance(
                exc,
                ReportExecutionException,
            ):
                raise

            raise ReportExecutionException(
                "Report query execution failed."
            ) from exc

        self._validate_result(
            result
        )

        return result

    def _validate_request(
        self,
        request: ReportExecutionRequest,
    ) -> None:
        """
        Validate the execution request.
        """

        if not isinstance(
            request,
            ReportExecutionRequest,
        ):
            raise ValueError(
                "Report execution request must be a "
                "ReportExecutionRequest instance."
            )

    def _execute_query(
        self,
        provider: Any,
        query: Any,
        parameters: dict[str, Any],
        context: ReportExecutionContext,
    ) -> ReportQueryResult:
        """
        Delegate query execution to the configured executor.

        Execution parameters and execution context are passed
        through without changing their semantic meaning.

        The method intentionally does not interpret the result.
        Result interpretation remains the responsibility of the
        query executor.
        """

        return self.query_executor.execute(
            provider,
            query,
            parameters=parameters,
            context=context,
        )

    def _validate_result(
        self,
        result: ReportQueryResult,
    ) -> None:
        """
        Validate the result returned by the query executor.

        SUCCESS, EMPTY, and FAILED are all valid standardized
        execution outcomes.

        Raises:
            ReportExecutionException:
                When the executor returns an invalid object.
        """

        if not isinstance(
            result,
            ReportQueryResult,
        ):
            raise ReportExecutionException(
                "Report query executor returned "
                "an invalid result."
            )


__all__ = [
    "ReportExecutionService",
]
