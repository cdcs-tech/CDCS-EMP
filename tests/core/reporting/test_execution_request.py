"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report execution request contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportExecutionContext,
    ReportExecutionRequest,
    ReportQuery,
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
