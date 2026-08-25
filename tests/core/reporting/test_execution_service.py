"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

Report execution service contract tests.
"""

from __future__ import annotations

import pytest
from typing import cast

from app.core.data import QueryOptions

from app.core.reporting import (
    ReportAuthorizationDecision,
    ReportAuthorizationOperation,
    ReportAuthorizationRequest,
    ReportAuthorizationResource,
    ReportAuthorizationSubject,
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
    ReportingAuthorizationAdapter,
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
    Concrete query executor used in execution-service tests.

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

    The default execution context represents an identified
    requesting subject so that normal execution tests pass
    through the authorization boundary.
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
            else ReportExecutionContext(
                requested_by="user-001",
            )
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


def create_service(
    authorization_evaluator=None,
):
    """
    Create a service with a registered provider,
    authorization adapter, and concrete query executor.
    """

    provider = ExampleReportDataProvider()

    registry = ReportDataProviderRegistry(
        providers=[
            provider,
        ]
    )

    executor = ExampleReportQueryExecutor()

    if authorization_evaluator is None:

        authorization_evaluator = (
            lambda request, permission: True
        )

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=authorization_evaluator,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
        authorization_adapter=authorization_adapter,
    )

    return (
        service,
        provider,
        executor,
        authorization_adapter,
    )


def test_execution_service_requires_provider_registry():

    executor = ExampleReportQueryExecutor()

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    with pytest.raises(
        ValueError,
        match="ReportDataProviderRegistry",
    ):
        ReportExecutionService(
            provider_registry=cast(
                ReportDataProviderRegistry,
                None,
            ),
            query_executor=executor,
            authorization_adapter=authorization_adapter,
        )


def test_execution_service_requires_query_executor():

    registry = ReportDataProviderRegistry()

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    with pytest.raises(
        ValueError,
        match="ReportQueryExecutor",
    ):
        ReportExecutionService(
            provider_registry=registry,
            query_executor=cast(
                ReportQueryExecutor,
                None,
            ),
            authorization_adapter=authorization_adapter,
        )


def test_execution_service_requires_authorization_adapter():

    registry = ReportDataProviderRegistry()

    executor = ExampleReportQueryExecutor()

    with pytest.raises(
        ValueError,
        match="ReportingAuthorizationAdapter",
    ):
        ReportExecutionService(
            provider_registry=registry,
            query_executor=executor,
            authorization_adapter=cast(
                ReportingAuthorizationAdapter,
                None,
            ),
        )


def test_execution_service_rejects_invalid_registry():

    executor = ExampleReportQueryExecutor()

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    with pytest.raises(
        ValueError,
        match="ReportDataProviderRegistry",
    ):
        ReportExecutionService(
            provider_registry=cast(
                ReportDataProviderRegistry,
                "invalid",
            ),
            query_executor=executor,
            authorization_adapter=authorization_adapter,
        )


def test_execution_service_rejects_invalid_executor():

    registry = ReportDataProviderRegistry()

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    with pytest.raises(
        ValueError,
        match="ReportQueryExecutor",
    ):
        ReportExecutionService(
            provider_registry=registry,
            query_executor=cast(
                ReportQueryExecutor,
                "invalid",
            ),
            authorization_adapter=authorization_adapter,
        )


def test_execution_service_rejects_invalid_authorization_adapter():

    registry = ReportDataProviderRegistry()

    executor = ExampleReportQueryExecutor()

    with pytest.raises(
        ValueError,
        match="ReportingAuthorizationAdapter",
    ):
        ReportExecutionService(
            provider_registry=registry,
            query_executor=executor,
            authorization_adapter=cast(
                ReportingAuthorizationAdapter,
                "invalid",
            ),
        )


def test_execution_service_accepts_valid_dependencies():

    service, _, _, _ = create_service()

    assert isinstance(
        service,
        ReportExecutionService,
    )


def test_execution_service_rejects_invalid_request():

    service, _, _, _ = create_service()

    with pytest.raises(
        ValueError,
        match="Report execution request",
    ):
        service.execute(
            cast(
                ReportExecutionRequest,
                "invalid",
            )
        )


def test_execution_service_resolves_provider():

    service, provider, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, executor, _ = (
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

    service, _, _, _ = create_service()

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

    service, _, _, _ = create_service()

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

    service, _, _, _ = create_service()

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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
        authorization_adapter=authorization_adapter,
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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
        authorization_adapter=authorization_adapter,
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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
        authorization_adapter=authorization_adapter,
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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=FixedResultExecutor(),
        authorization_adapter=authorization_adapter,
    )

    result = service.execute(
        create_request()
    )

    assert result is expected_result


def test_execution_service_rejects_unsupported_query():

    service, _, _, _ = create_service()

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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=FailingExecutor(),
        authorization_adapter=authorization_adapter,
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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=FailingExecutor(),
        authorization_adapter=authorization_adapter,
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

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: True,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=InvalidExecutor(),
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        ReportExecutionException,
        match="invalid result",
    ):
        service.execute(
            create_request()
        )


# ---------------------------------------------------------------------------
# Stage 1.16.8.4
# Report Execution Authorization Integration
# ---------------------------------------------------------------------------


def test_execution_service_authorizes_before_execution():

    calls = []

    def evaluator(
        request,
        permission_code,
    ):
        calls.append(
            (
                "authorize",
                request,
                permission_code,
            )
        )

        return True

    service, provider, executor, _ = (
        create_service(
            authorization_evaluator=evaluator,
        )
    )

    context = ReportExecutionContext(
        requested_by="user-001",
    )

    service.execute(
        create_request(
            context=context,
        )
    )

    assert len(calls) == 1

    assert (
        calls[0][0]
        == "authorize"
    )

    assert (
        calls[0][2]
        == "reporting.report.execute"
    )

    assert executor.provider is provider


def test_execution_service_builds_correct_authorization_request():

    captured = {}

    def evaluator(
        request,
        permission_code,
    ):
        captured["request"] = request
        captured["permission"] = permission_code

        return True

    service, _, _, _ = create_service(
        authorization_evaluator=evaluator,
    )

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="api",
        metadata={
            "environment": "test",
        },
    )

    query = create_query()

    service.execute(
        create_request(
            query=query,
            context=context,
        )
    )

    authorization_request = (
        captured["request"]
    )

    assert isinstance(
        authorization_request,
        ReportAuthorizationRequest,
    )

    assert (
        authorization_request.subject.identifier
        == "user-001"
    )

    assert (
        authorization_request.operation
        == ReportAuthorizationOperation.EXECUTE
    )

    assert (
        authorization_request.resource.resource_type
        == "report"
    )

    assert (
        authorization_request.resource.identifier
        == query.identifier
    )

    assert (
        authorization_request.resource.metadata[
            "report_code"
        ]
        == query.report_code
    )

    assert (
        authorization_request.context.metadata[
            "correlation_id"
        ]
        == "corr-001"
    )

    assert (
        authorization_request.context.metadata[
            "source"
        ]
        == "api"
    )

    assert (
        authorization_request.context.metadata[
            "environment"
        ]
        == "test"
    )

    assert (
        captured["permission"]
        == "reporting.report.execute"
    )


def test_execution_service_rejects_missing_requesting_subject():

    service, _, _, _ = create_service()

    context = ReportExecutionContext()

    with pytest.raises(
        ReportExecutionException,
        match="identified requesting subject",
    ):
        service.execute(
            create_request(
                context=context,
            )
        )


def test_execution_service_denied_authorization_stops_execution():

    service, _, executor, _ = create_service(
        authorization_evaluator=(
            lambda request, permission: False
        ),
    )

    context = ReportExecutionContext(
        requested_by="user-001",
    )

    with pytest.raises(
        ReportExecutionException,
        match="Reporting authorization denied",
    ):
        service.execute(
            create_request(
                context=context,
            )
        )

    assert executor.provider is None
    assert executor.query is None


def test_execution_service_preserves_authorization_denial_reason():

    def evaluator(
        request,
        permission_code,
    ):
        return ReportAuthorizationDecision(
            status="deny",
            reason=(
                "User lacks report execution permission."
            ),
            metadata={
                "permission_code": permission_code,
            },
        )

    service, _, executor, _ = create_service(
        authorization_evaluator=evaluator,
    )

    context = ReportExecutionContext(
        requested_by="user-001",
    )

    with pytest.raises(
        ReportExecutionException,
        match="User lacks report execution permission",
    ):
        service.execute(
            create_request(
                context=context,
            )
        )

    assert executor.provider is None
    assert executor.query is None


def test_execution_service_wraps_authorization_failure():

    def evaluator(
        request,
        permission_code,
    ):
        raise RuntimeError(
            "security backend unavailable"
        )

    service, _, executor, _ = create_service(
        authorization_evaluator=evaluator,
    )

    context = ReportExecutionContext(
        requested_by="user-001",
    )

    with pytest.raises(
        ReportExecutionException,
        match="Report execution authorization failed",
    ) as exc_info:

        service.execute(
            create_request(
                context=context,
            )
        )

    assert isinstance(
        exc_info.value.__cause__,
        RuntimeError,
    )

    assert executor.provider is None
    assert executor.query is None


def test_execution_service_authorization_receives_report_resource():

    captured = {}

    def evaluator(
        request,
        permission_code,
    ):
        captured["request"] = request
        return True

    service, _, _, _ = create_service(
        authorization_evaluator=evaluator,
    )

    service.execute(
        create_request()
    )

    request = captured["request"]

    assert isinstance(
        request.resource,
        ReportAuthorizationResource,
    )

    assert (
        request.resource.canonical_identifier
        == "report:EXAMPLE"
    )


def test_execution_service_authorization_receives_subject():

    captured = {}

    def evaluator(
        request,
        permission_code,
    ):
        captured["request"] = request
        return True

    service, _, _, _ = create_service(
        authorization_evaluator=evaluator,
    )

    context = ReportExecutionContext(
        requested_by="user-001",
    )

    service.execute(
        create_request(
            context=context,
        )
    )

    request = captured["request"]

    assert isinstance(
        request.subject,
        ReportAuthorizationSubject,
    )

    assert (
        request.subject.identifier
        == "user-001"
    )

    assert (
        request.subject.canonical_identifier
        == "user:user-001"
    )


def test_execution_service_authorization_receives_execute_operation():

    captured = {}

    def evaluator(
        request,
        permission_code,
    ):
        captured["request"] = request
        return True

    service, _, _, _ = create_service(
        authorization_evaluator=evaluator,
    )

    service.execute(
        create_request()
    )

    request = captured["request"]

    assert (
        request.operation
        == ReportAuthorizationOperation.EXECUTE
    )

    assert (
        request.operation.code
        == "execute"
    )


def test_execution_service_authorization_receives_execution_context():

    captured = {}

    def evaluator(
        request,
        permission_code,
    ):
        captured["request"] = request
        return True

    service, _, _, _ = create_service(
        authorization_evaluator=evaluator,
    )

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="web",
        metadata={
            "environment": "test",
            "tenant": "cdcs",
        },
    )

    service.execute(
        create_request(
            context=context,
        )
    )

    authorization_context = (
        captured["request"].context
    )

    assert (
        authorization_context.metadata[
            "correlation_id"
        ]
        == "corr-001"
    )

    assert (
        authorization_context.metadata[
            "source"
        ]
        == "web"
    )

    assert (
        authorization_context.metadata[
            "environment"
        ]
        == "test"
    )

    assert (
        authorization_context.metadata[
            "tenant"
        ]
        == "cdcs"
    )


def test_execution_service_authorization_failure_prevents_provider_resolution():

    calls = []

    class TrackingProviderRegistry(
        ReportDataProviderRegistry,
    ):

        def resolve(
            self,
            query,
        ):
            calls.append(
                "resolve"
            )

            return super().resolve(
                query
            )

    provider = ExampleReportDataProvider()

    registry = TrackingProviderRegistry(
        providers=[
            provider,
        ]
    )

    executor = ExampleReportQueryExecutor()

    authorization_adapter = (
        ReportingAuthorizationAdapter(
            evaluator=lambda request, permission: False,
        )
    )

    service = ReportExecutionService(
        provider_registry=registry,
        query_executor=executor,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        ReportExecutionException,
        match="Reporting authorization denied",
    ):
        service.execute(
            create_request()
        )

    assert calls == []


def test_execution_service_authorization_failure_prevents_query_execution():

    service, _, executor, _ = create_service(
        authorization_evaluator=(
            lambda request, permission: False
        ),
    )

    with pytest.raises(
        ReportExecutionException,
        match="Reporting authorization denied",
    ):
        service.execute(
            create_request()
        )

    assert executor.provider is None
    assert executor.query is None


def test_execution_service_authorization_failure_is_execution_boundary():

    service, _, _, _ = create_service(
        authorization_evaluator=(
            lambda request, permission: False
        ),
    )

    with pytest.raises(
        ReportExecutionException,
    ) as exc_info:

        service.execute(
            create_request()
        )

    assert (
        str(exc_info.value)
        == "Reporting authorization denied."
    )


def test_execution_service_authorization_decision_is_not_exposed_as_result():

    service, _, _, _ = create_service(
        authorization_evaluator=(
            lambda request, permission: False
        ),
    )

    with pytest.raises(
        ReportExecutionException,
    ):
        service.execute(
            create_request()
        )
