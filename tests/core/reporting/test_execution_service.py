"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report execution service contract tests.
"""

from __future__ import annotations

import pytest
from typing import cast

from app.core.data import QueryOptions

from app.core.reporting import (
    ReportDataProvider,
    ReportDataProviderRegistry,
    ReportExecutionContext,
    ReportExecutionException,
    ReportExecutionRequest,
    ReportExecutionService,
    ReportFilter,
    ReportFilterCollection,
    ReportFilterOperator,
    ReportQuery,
    ReportQueryExecutor,
    ReportQueryResult,
    ReportQueryResultStatus,
    ReportSort,
    ReportSortCollection,
    ReportSortDirection,
)


class ExampleReportDataProvider(
    ReportDataProvider,
):
    """
    Concrete data provider used by execution-service tests.
    """

    @property
    def name(
        self,
    ) -> str:
        return "example"

    def supports(
        self,
        query: ReportQuery,
    ) -> bool:
        return (
            query.identifier
            == "EXAMPLE"
        )

    def execute(
        self,
        query: ReportQuery,
        options=None,
    ):
        return {
            "report_code": query.report_code,
            "metadata": query.to_dict()["metadata"],
        }


class ExampleReportQueryExecutor(
    ReportQueryExecutor,
):
    """
    Concrete query executor used by execution-service tests.

    The executor deliberately accepts the complete
    provider-neutral execution boundary exposed by the
    reporting execution service.
    """

    def __init__(
        self,
    ):
        self.provider = None
        self.query = None
        self.options = None
        self.parameters = None
        self.context = None
        self.filters = None
        self.sorting = None

    def execute(
        self,
        provider: ReportDataProvider,
        query: ReportQuery,
        options=None,
        parameters=None,
        context=None,
        filters=None,
        sorting=None,
    ) -> ReportQueryResult:

        self.provider = provider
        self.query = query
        self.options = options
        self.parameters = parameters
        self.context = context
        self.filters = filters
        self.sorting = sorting

        data = provider.execute(
            query,
            options,
        )

        status = (
            ReportQueryResultStatus.EMPTY
            if not data
            else ReportQueryResultStatus.SUCCESS
        )

        return ReportQueryResult(
            query=query,
            data=data,
            status=status,
            metadata={
                "provider": provider.name,
            },
        )


class EmptyResultQueryExecutor(
    ExampleReportQueryExecutor,
):
    """
    Executor used to verify preservation of EMPTY results.
    """

    def execute(
        self,
        provider,
        query,
        options=None,
        parameters=None,
        context=None,
        filters=None,
        sorting=None,
    ):

        self.provider = provider
        self.query = query
        self.options = options
        self.parameters = parameters
        self.context = context
        self.filters = filters
        self.sorting = sorting

        return ReportQueryResult(
            query=query,
            data=None,
            status=ReportQueryResultStatus.EMPTY,
            metadata={
                "provider": provider.name,
            },
            message="No report data available.",
        )


class FailedResultQueryExecutor(
    ExampleReportQueryExecutor,
):
    """
    Executor used to verify preservation of FAILED results.
    """

    def execute(
        self,
        provider,
        query,
        options=None,
        parameters=None,
        context=None,
        filters=None,
        sorting=None,
    ):

        self.provider = provider
        self.query = query
        self.options = options
        self.parameters = parameters
        self.context = context
        self.filters = filters
        self.sorting = sorting

        return ReportQueryResult(
            query=query,
            data=None,
            status=ReportQueryResultStatus.FAILED,
            metadata={
                "provider": provider.name,
            },
            message="Report provider failed.",
            error="Provider returned a failed result.",
        )


def create_query() -> ReportQuery:
    """
    Create a standard test query.
    """

    return ReportQuery(
        report_code="EXAMPLE",
        metadata={
            "source": "test",
        },
    )


def create_request(
    query=None,
    parameters=None,
    context=None,
    query_options=None,
    filters=None,
    sorting=None,
) -> ReportExecutionRequest:
    """
    Create a standard report execution request.
    """

    return ReportExecutionRequest(
        query=query or create_query(),
        parameters=(
            parameters
            if parameters is not None
            else {}
        ),
        context=(
            context
            if context is not None
            else ReportExecutionContext()
        ),
        query_options=query_options,
        filters=(
            filters
            if filters is not None
            else ReportFilterCollection()
        ),
        sorting=(
            sorting
            if sorting is not None
            else ReportSortCollection()
        ),
    )


def create_service():
    """
    Create a service with a registered provider and
    concrete query executor.
    """

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    executor = ExampleReportQueryExecutor()

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
    )

    return (
        service,
        provider,
        executor,
    )


def test_execution_service_requires_provider_registry():

    executor = ExampleReportQueryExecutor()

    with pytest.raises(
        ValueError,
        match="ReportDataProviderRegistry",
    ):
        ReportExecutionService(
            provider_registry=cast(ReportDataProviderRegistry, None),
            query_executor=executor,
        )


def test_execution_service_requires_query_executor():

    registry = ReportDataProviderRegistry()

    with pytest.raises(
        ValueError,
        match="ReportQueryExecutor",
    ):
        ReportExecutionService(
            provider_registry=registry,
            query_executor=cast(ReportQueryExecutor, None),
        )


def test_execution_service_rejects_invalid_registry():

    executor = ExampleReportQueryExecutor()

    with pytest.raises(
        ValueError,
        match="ReportDataProviderRegistry",
    ):
        ReportExecutionService(
            provider_registry=cast(ReportDataProviderRegistry, "invalid"),
            query_executor=executor,
        )


def test_execution_service_rejects_invalid_executor():

    registry = ReportDataProviderRegistry()

    with pytest.raises(
        ValueError,
        match="ReportQueryExecutor",
    ):
        ReportExecutionService(
            provider_registry=registry,
            query_executor=cast(ReportQueryExecutor, "invalid"),
        )


def test_execution_service_accepts_valid_dependencies():

    service, _, _ = create_service()

    assert isinstance(
        service,
        ReportExecutionService,
    )


def test_execution_service_rejects_invalid_request():

    service, _, _ = create_service()

    with pytest.raises(
        ValueError,
        match="Report execution request",
    ):
        service.execute(
            cast(ReportExecutionRequest, "invalid")
        )


def test_execution_service_resolves_provider():

    service, provider, executor = (
        create_service()
    )

    result = service.execute(
        create_request()
    )

    assert (
        executor.provider
        is provider
    )

    assert isinstance(
        result,
        ReportQueryResult,
    )


def test_execution_service_passes_query_to_executor():

    service, _, executor = (
        create_service()
    )

    query = create_query()

    request = create_request(
        query=query,
    )

    result = service.execute(
        request
    )

    assert (
        executor.query
        is query
    )

    assert (
        result.query
        is query
    )


def test_execution_service_passes_parameters_to_executor():

    service, _, executor = (
        create_service()
    )

    parameters = {
        "year": 2026,
        "department": "Finance",
    }

    service.execute(
        create_request(
            parameters=parameters,
        )
    )

    assert (
        executor.parameters
        == parameters
    )


def test_execution_service_copies_parameter_boundary():

    service, _, executor = (
        create_service()
    )

    parameters = {
        "year": 2026,
    }

    request = create_request(
        parameters=parameters,
    )

    parameters["changed"] = True

    service.execute(
        request
    )

    assert (
        executor.parameters
        == {
            "year": 2026,
        }
    )


def test_execution_service_passes_context_to_executor():

    service, _, executor = (
        create_service()
    )

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="web",
        metadata={
            "environment": "test",
        },
    )

    service.execute(
        create_request(
            context=context,
        )
    )

    assert (
        executor.context
        is context
    )


def test_execution_service_preserves_execution_context_values():

    service, _, executor = (
        create_service()
    )

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="api",
    )

    service.execute(
        create_request(
            context=context,
        )
    )

    assert (
        executor.context.correlation_id
        == "corr-001"
    )

    assert (
        executor.context.requested_by
        == "user-001"
    )

    assert (
        executor.context.source
        == "api"
    )


def test_execution_service_passes_query_options_to_executor():

    service, _, executor = (
        create_service()
    )

    query_options = QueryOptions(
        page=2,
        page_size=25,
        sort_by="name",
        sort_direction="desc",
        filters={
            "is_active": True,
        },
    )

    service.execute(
        create_request(
            query_options=query_options,
        )
    )

    assert (
        executor.options
        is query_options
    )


def test_execution_service_passes_filters_to_executor():

    service, _, executor = (
        create_service()
    )

    filters = ReportFilterCollection(
        filters=[
            ReportFilter(
                field="department",
                operator=ReportFilterOperator.EQUALS,
                value="Finance",
            ),
            ReportFilter(
                field="is_active",
                operator=ReportFilterOperator.EQUALS,
                value=True,
            ),
        ]
    )

    service.execute(
        create_request(
            filters=filters,
        )
    )

    assert (
        executor.filters
        is filters
    )


def test_execution_service_passes_sorting_to_executor():

    service, _, executor = (
        create_service()
    )

    sorting = ReportSortCollection(
        sorts=[
            ReportSort(
                field="name",
                direction=ReportSortDirection.ASCENDING,
            ),
            ReportSort(
                field="created_at",
                direction=ReportSortDirection.DESCENDING,
            ),
        ]
    )

    service.execute(
        create_request(
            sorting=sorting,
        )
    )

    assert (
        executor.sorting
        is sorting
    )


def test_execution_service_passes_complete_execution_request():

    service, _, executor = (
        create_service()
    )

    query = create_query()

    parameters = {
        "year": 2026,
        "department": "Finance",
    }

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="api",
    )

    query_options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
    )

    filters = ReportFilterCollection(
        filters=[
            ReportFilter(
                field="department",
                operator=ReportFilterOperator.EQUALS,
                value="Finance",
            ),
        ]
    )

    sorting = ReportSortCollection(
        sorts=[
            ReportSort(
                field="name",
                direction=ReportSortDirection.ASCENDING,
            ),
        ]
    )

    request = create_request(
        query=query,
        parameters=parameters,
        context=context,
        query_options=query_options,
        filters=filters,
        sorting=sorting,
    )

    result = service.execute(
        request
    )

    assert executor.provider is not None
    assert executor.query is query
    assert executor.options is query_options
    assert executor.parameters == parameters
    assert executor.context is context
    assert executor.filters is filters
    assert executor.sorting is sorting

    assert isinstance(
        result,
        ReportQueryResult,
    )


def test_execution_service_returns_success_result():

    service, _, _ = create_service()

    result = service.execute(
        create_request()
    )

    assert isinstance(
        result,
        ReportQueryResult,
    )

    assert (
        result.status
        == ReportQueryResultStatus.SUCCESS
    )

    assert (
        result.is_success
        is True
    )


def test_execution_service_preserves_success_result_data():

    service, _, _ = create_service()

    result = service.execute(
        create_request()
    )

    assert (
        result.data["report_code"]
        == "EXAMPLE"
    )

    assert (
        result.data["metadata"]["source"]
        == "test"
    )


def test_execution_service_preserves_success_result_metadata():

    service, _, _ = create_service()

    result = service.execute(
        create_request()
    )

    assert (
        result.metadata["provider"]
        == "example"
    )


def test_execution_service_preserves_empty_result():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    executor = EmptyResultQueryExecutor()

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
    )

    result = service.execute(
        create_request()
    )

    assert isinstance(
        result,
        ReportQueryResult,
    )

    assert (
        result.status
        == ReportQueryResultStatus.EMPTY
    )

    assert (
        result.is_empty
        is True
    )

    assert (
        result.data
        is None
    )

    assert (
        result.message
        == "No report data available."
    )


def test_execution_service_preserves_failed_result():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    executor = FailedResultQueryExecutor()

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
    )

    result = service.execute(
        create_request()
    )

    assert isinstance(
        result,
        ReportQueryResult,
    )

    assert (
        result.status
        == ReportQueryResultStatus.FAILED
    )

    assert (
        result.is_failed
        is True
    )

    assert (
        result.error
        == "Provider returned a failed result."
    )


def test_execution_service_does_not_raise_for_failed_result():

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    executor = FailedResultQueryExecutor()

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
    )

    result = service.execute(
        create_request()
    )

    assert result.is_failed


def test_execution_service_preserves_result_identity():

    expected_result = ReportQueryResult(
        query=create_query(),
        data={
            "rows": [
                {
                    "id": 1,
                }
            ],
        },
        status=ReportQueryResultStatus.SUCCESS,
    )

    class FixedResultExecutor(
        ReportQueryExecutor,
    ):

        def execute(
            self,
            provider,
            query,
            options=None,
            parameters=None,
            context=None,
            filters=None,
            sorting=None,
        ):
            return expected_result

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=FixedResultExecutor(),
    )

    result = service.execute(
        create_request()
    )

    assert result is expected_result


def test_execution_service_rejects_unsupported_query():

    service, _, _ = create_service()

    request = create_request(
        query=ReportQuery(
            report_code="UNKNOWN",
        ),
    )

    with pytest.raises(
        ReportExecutionException,
        match="Report query execution failed",
    ):
        service.execute(
            request
        )


def test_execution_service_preserves_execution_exception():

    class FailingExecutor(
        ReportQueryExecutor,
    ):

        def execute(
            self,
            provider,
            query,
            options=None,
            parameters=None,
            context=None,
            filters=None,
            sorting=None,
        ):
            raise ReportExecutionException(
                "Expected execution failure."
            )

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=FailingExecutor(),
    )

    with pytest.raises(
        ReportExecutionException,
        match="Expected execution failure",
    ):
        service.execute(
            create_request()
        )


def test_execution_service_wraps_unexpected_executor_failure():

    class FailingExecutor(
        ReportQueryExecutor,
    ):

        def execute(
            self,
            provider,
            query,
            options=None,
            parameters=None,
            context=None,
            filters=None,
            sorting=None,
        ):
            raise RuntimeError(
                "Unexpected provider failure."
            )

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=FailingExecutor(),
    )

    with pytest.raises(
        ReportExecutionException,
        match="Report query execution failed",
    ) as exc_info:

        service.execute(
            create_request()
        )

    assert isinstance(
        exc_info.value.__cause__,
        RuntimeError,
    )


def test_execution_service_rejects_invalid_executor_result():

    class InvalidExecutor(
        ReportQueryExecutor,
    ):

        def execute(
            self,
            provider,
            query,
            options=None,
            parameters=None,
            context=None,
            filters=None,
            sorting=None,
        ):
            return {
                "invalid": "result",
            }

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=InvalidExecutor(),
    )

    with pytest.raises(
        ReportExecutionException,
        match="invalid result",
    ):
        service.execute(
            create_request()
        )
