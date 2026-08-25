"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Report execution service contract.
"""

from __future__ import annotations

from typing import Any

from app.core.reporting.authorization import (
    ReportAuthorizationContext,
    ReportAuthorizationOperation,
    ReportAuthorizationRequest,
    ReportAuthorizationResource,
    ReportAuthorizationSubject,
)
from app.core.reporting.authorization_adapter import (
    ReportingAuthorizationAdapter,
)
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
    - execution authorization
    - provider resolution
    - execution-option propagation
    - execution-parameter propagation
    - execution-context propagation
    - reporting-filter propagation
    - reporting-sorting propagation
    - query execution
    - standardized execution-result validation
    - execution failure translation

    Authorization is evaluated before provider resolution
    and query execution.

    The service preserves ReportQueryResult outcomes
    produced by the query executor, including SUCCESS,
    EMPTY, and FAILED results.

    Governance, auditing, telemetry, transaction
    management, persistence, and presentation remain
    outside this service.
    """

    def __init__(
        self,
        provider_registry: ReportDataProviderRegistry,
        query_executor: ReportQueryExecutor,
        authorization_adapter: ReportingAuthorizationAdapter,
    ) -> None:
        """
        Initialize the report execution service.
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

        if not isinstance(
            authorization_adapter,
            ReportingAuthorizationAdapter,
        ):
            raise ValueError(
                "A ReportingAuthorizationAdapter is required."
            )

        self.provider_registry = (
            provider_registry
        )

        self.query_executor = (
            query_executor
        )

        self.authorization_adapter = (
            authorization_adapter
        )

    def execute(
        self,
        request: ReportExecutionRequest,
    ) -> ReportQueryResult:
        """
        Execute a provider-neutral report execution request.

        The service:

        1. validates the execution request,
        2. validates the execution subject,
        3. builds the provider-neutral authorization request,
        4. evaluates execution authorization,
        5. resolves the appropriate data provider,
        6. propagates all execution-boundary contracts,
        7. delegates execution to the query executor,
        8. validates the returned execution result, and
        9. returns the standardized ReportQueryResult.

        Authorization is evaluated before provider resolution
        and query execution.

        SUCCESS, EMPTY, and FAILED query results are valid
        execution outcomes and are returned unchanged.

        Exceptions raised during authorization, provider
        resolution, or query execution are translated into
        the reporting execution exception boundary.
        """

        self._validate_request(
            request
        )

        query = request.query

        parameters = dict(
            request.parameters
        )

        context = request.context

        query_options = request.query_options

        filters = request.filters

        sorting = request.sorting

        try:

            authorization_request = (
                self._build_authorization_request(
                    query=query,
                    context=context,
                )
            )

            self._authorize(
                authorization_request
            )

            provider = (
                self.provider_registry.resolve(
                    query
                )
            )

            result = self._execute_query(
                provider=provider,
                query=query,
                options=query_options,
                parameters=parameters,
                context=context,
                filters=filters,
                sorting=sorting,
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

    def _build_authorization_request(
        self,
        query: Any,
        context: ReportExecutionContext,
    ) -> ReportAuthorizationRequest:
        """
        Build the provider-neutral authorization request
        required for report execution.
        """

        if context.requested_by is None:

            raise ReportExecutionException(
                "Report execution requires an "
                "identified requesting subject."
            )

        subject = ReportAuthorizationSubject(
            identifier=context.requested_by,
        )

        resource = ReportAuthorizationResource(
            resource_type="report",
            identifier=query.identifier,
            metadata={
                "report_code": query.report_code,
            },
        )

        authorization_context = (
            ReportAuthorizationContext(
                metadata={
                    "correlation_id": (
                        context.correlation_id
                    ),
                    "source": context.source,
                    **dict(
                        context.metadata
                    ),
                }
            )
        )

        return ReportAuthorizationRequest(
            subject=subject,
            operation=(
                ReportAuthorizationOperation.EXECUTE
            ),
            resource=resource,
            context=authorization_context,
        )

    def _authorize(
        self,
        request: ReportAuthorizationRequest,
    ) -> None:
        """
        Evaluate report execution authorization.

        A denied authorization decision prevents all
        downstream report execution.

        Authorization failures are translated into the
        reporting execution exception boundary.
        """

        try:

            decision = (
                self.authorization_adapter.authorize(
                    request
                )
            )

        except Exception as exc:

            raise ReportExecutionException(
                "Report execution authorization failed."
            ) from exc

        if not decision.is_allowed:

            reason = (
                decision.reason
                or "Report execution authorization denied."
            )

            raise ReportExecutionException(
                reason
            )

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
        options: Any,
        parameters: dict[str, Any],
        context: ReportExecutionContext,
        filters: Any,
        sorting: Any,
    ) -> ReportQueryResult:
        """
        Delegate query execution to the configured executor.

        All provider-neutral execution contracts are passed
        through without changing their semantic meaning.

        The method intentionally does not interpret the result.
        Result interpretation remains the responsibility of the
        query executor.
        """

        return self.query_executor.execute(
            provider,
            query,
            options=options,
            parameters=parameters,
            context=context,
            filters=filters,
            sorting=sorting,
        )

    def _validate_result(
        self,
        result: ReportQueryResult,
    ) -> None:
        """
        Validate the result returned by the query executor.
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
