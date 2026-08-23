"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report execution request contract tests.
"""

from __future__ import annotations

import pytest

from app.core.data import QueryOptions

from app.core.reporting import (
    ReportExecutionContext,
    ReportExecutionRequest,
    ReportFilter,
    ReportFilterCollection,
    ReportFilterOperator,
    ReportQuery,
    ReportSort,
    ReportSortCollection,
    ReportSortDirection,
)


def create_query() -> ReportQuery:

    return ReportQuery(
        report_code="SALES_SUMMARY",
        metadata={
            "module": "finance",
        },
    )


def test_execution_request_defaults():

    request = ReportExecutionRequest(
        query=create_query(),
    )

    assert (
        request.query.report_code
        == "SALES_SUMMARY"
    )

    assert (
        request.parameters
        == {}
    )

    assert isinstance(
        request.context,
        ReportExecutionContext,
    )

    assert (
        request.context.metadata
        == {}
    )

    assert (
        request.query_options
        is None
    )

    assert isinstance(
        request.filters,
        ReportFilterCollection,
    )

    assert (
        len(request.filters)
        == 0
    )

    assert isinstance(
        request.sorting,
        ReportSortCollection,
    )

    assert (
        len(request.sorting)
        == 0
    )


def test_execution_request_accepts_parameters():

    request = ReportExecutionRequest(
        query=create_query(),
        parameters={
            "year": 2026,
            "department": "Finance",
        },
    )

    assert (
        request.parameters["year"]
        == 2026
    )

    assert (
        request.parameters["department"]
        == "Finance"
    )


def test_execution_request_accepts_context():

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="web",
    )

    request = ReportExecutionRequest(
        query=create_query(),
        context=context,
    )

    assert (
        request.context
        is context
    )


def test_execution_request_accepts_query_options():

    options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
    )

    request = ReportExecutionRequest(
        query=create_query(),
        query_options=options,
    )

    assert (
        request.query_options
        is options
    )


def test_execution_request_accepts_filters():

    filters = ReportFilterCollection(
        filters=[
            ReportFilter(
                field="status",
                operator=ReportFilterOperator.EQUALS,
                value="active",
            ),
        ]
    )

    request = ReportExecutionRequest(
        query=create_query(),
        filters=filters,
    )

    assert (
        request.filters
        is filters
    )


def test_execution_request_accepts_sorting():

    sorting = ReportSortCollection(
        sorts=[
            ReportSort(
                field="name",
                direction=ReportSortDirection.ASCENDING,
            ),
        ]
    )

    request = ReportExecutionRequest(
        query=create_query(),
        sorting=sorting,
    )

    assert (
        request.sorting
        is sorting
    )


def test_execution_request_accepts_complete_execution_boundary():

    options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
    )

    filters = ReportFilterCollection(
        filters=[
            ReportFilter(
                field="status",
                operator=ReportFilterOperator.EQUALS,
                value="active",
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

    context = ReportExecutionContext(
        correlation_id="corr-001",
        source="api",
    )

    request = ReportExecutionRequest(
        query=create_query(),
        parameters={
            "year": 2026,
        },
        context=context,
        query_options=options,
        filters=filters,
        sorting=sorting,
    )

    assert request.query.report_code == "SALES_SUMMARY"
    assert request.parameters["year"] == 2026
    assert request.context is context
    assert request.query_options is options
    assert request.filters is filters
    assert request.sorting is sorting


def test_execution_request_accepts_parameters_and_context():

    context = ReportExecutionContext(
        correlation_id="corr-001",
        source="api",
        metadata={
            "environment": "test",
        },
    )

    request = ReportExecutionRequest(
        query=create_query(),
        parameters={
            "year": 2026,
        },
        context=context,
    )

    assert (
        request.report_code
        == "SALES_SUMMARY"
    )

    assert (
        request.identifier
        == "SALES_SUMMARY"
    )

    assert (
        request.parameters["year"]
        == 2026
    )

    assert (
        request.context.correlation_id
        == "corr-001"
    )


def test_execution_request_rejects_invalid_query():

    with pytest.raises(
        ValueError,
        match="ReportQuery",
    ):

        ReportExecutionRequest(
            query="invalid",
        )


def test_execution_request_rejects_invalid_parameters():

    with pytest.raises(
        ValueError,
        match="parameters",
    ):

        ReportExecutionRequest(
            query=create_query(),
            parameters=[
                "invalid",
            ],
        )


def test_execution_request_rejects_invalid_context():

    with pytest.raises(
        ValueError,
        match="ReportExecutionContext",
    ):

        ReportExecutionRequest(
            query=create_query(),
            context="invalid",
        )


def test_execution_request_rejects_invalid_query_options():

    with pytest.raises(
        ValueError,
        match="query_options",
    ):

        ReportExecutionRequest(
            query=create_query(),
            query_options="invalid",
        )


def test_execution_request_rejects_invalid_filters():

    with pytest.raises(
        ValueError,
        match="ReportFilterCollection",
    ):

        ReportExecutionRequest(
            query=create_query(),
            filters="invalid",
        )


def test_execution_request_rejects_invalid_sorting():

    with pytest.raises(
        ValueError,
        match="ReportSortCollection",
    ):

        ReportExecutionRequest(
            query=create_query(),
            sorting="invalid",
        )


def test_execution_request_copies_parameters():

    parameters = {
        "year": 2026,
    }

    request = ReportExecutionRequest(
        query=create_query(),
        parameters=parameters,
    )

    parameters["changed"] = True

    assert (
        "changed"
        not in request.parameters
    )


def test_execution_request_to_dict():

    options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
    )

    request = ReportExecutionRequest(
        query=create_query(),
        parameters={
            "year": 2026,
            "department": "Finance",
        },
        context=ReportExecutionContext(
            correlation_id="corr-001",
            requested_by="user-001",
            source="web",
            metadata={
                "environment": "test",
            },
        ),
        query_options=options,
    )

    result = request.to_dict()

    assert (
        result["query"]["report_code"]
        == "SALES_SUMMARY"
    )

    assert (
        result["query"]["metadata"]["module"]
        == "finance"
    )

    assert (
        result["parameters"]["year"]
        == 2026
    )

    assert (
        result["parameters"]["department"]
        == "Finance"
    )

    assert (
        result["context"]["correlation_id"]
        == "corr-001"
    )

    assert (
        result["context"]["requested_by"]
        == "user-001"
    )

    assert (
        result["context"]["source"]
        == "web"
    )

    assert (
        result["context"]["metadata"]["environment"]
        == "test"
    )

    assert (
        result["query_options"]
        == options.to_dict()
    )

    assert (
        result["filters"]
        == []
    )

    assert (
        result["sorting"]
        == []
    )


def test_execution_request_is_immutable():

    request = ReportExecutionRequest(
        query=create_query(),
    )

    with pytest.raises(
        AttributeError
    ):

        request.query = create_query()


def test_execution_request_preserves_query_identity():

    query = create_query()

    request = ReportExecutionRequest(
        query=query,
    )

    assert (
        request.query
        is query
    )
