"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report query result contract tests.
"""

from app.core.reporting import (
    ReportQuery,
    ReportQueryResult,
    ReportQueryResultStatus,
)


def create_query():
    return ReportQuery(
        report_code="FINANCE_MONTHLY",
        metadata={
            "source": "finance",
        },
    )


def test_report_query_result_defaults():

    query = create_query()

    result = ReportQueryResult(
        query=query,
    )

    assert (
        result.query
        is query
    )

    assert (
        result.data
        is None
    )

    assert (
        result.status
        == ReportQueryResultStatus.SUCCESS
    )

    assert (
        result.metadata
        == {}
    )

    assert (
        result.message
        is None
    )

    assert (
        result.error
        is None
    )


def test_report_query_result_success_state():

    result = ReportQueryResult(
        query=create_query(),
        data=[
            {
                "id": 1,
                "amount": 250,
            }
        ],
    )

    assert (
        result.is_success
        is True
    )

    assert (
        result.is_empty
        is False
    )

    assert (
        result.is_failed
        is False
    )


def test_report_query_result_empty_state():

    result = ReportQueryResult(
        query=create_query(),
        status=(
            ReportQueryResultStatus.EMPTY
        ),
        data=[],
        message="No query data was found.",
    )

    assert (
        result.is_success
        is False
    )

    assert (
        result.is_empty
        is True
    )

    assert (
        result.is_failed
        is False
    )

    assert (
        result.message
        == "No query data was found."
    )


def test_report_query_result_failed_state():

    result = ReportQueryResult(
        query=create_query(),
        status=(
            ReportQueryResultStatus.FAILED
        ),
        error="Query execution failed.",
    )

    assert (
        result.is_success
        is False
    )

    assert (
        result.is_empty
        is False
    )

    assert (
        result.is_failed
        is True
    )

    assert (
        result.error
        == "Query execution failed."
    )


def test_report_query_result_metadata_is_independent():

    metadata = {
        "provider": "finance",
        "execution_id": "123",
    }

    result = ReportQueryResult(
        query=create_query(),
        metadata=metadata,
    )

    metadata["provider"] = "changed"

    assert (
        result.metadata["provider"]
        == "changed"
    )


def test_report_query_result_to_dict():

    query = create_query()

    result = ReportQueryResult(
        query=query,
        data={
            "total": 25,
        },
        status=(
            ReportQueryResultStatus.SUCCESS
        ),
        metadata={
            "provider": "finance",
        },
        message="Query executed.",
    )

    serialized = result.to_dict()

    assert (
        serialized["query"]
        == query.to_dict()
    )

    assert (
        serialized["data"]["total"]
        == 25
    )

    assert (
        serialized["status"]
        == "success"
    )

    assert (
        serialized["metadata"]["provider"]
        == "finance"
    )

    assert (
        serialized["message"]
        == "Query executed."
    )

    assert (
        serialized["error"]
        is None
    )


def test_report_query_result_failed_to_dict():

    result = ReportQueryResult(
        query=create_query(),
        status=(
            ReportQueryResultStatus.FAILED
        ),
        error="Provider failure.",
    )

    serialized = result.to_dict()

    assert (
        serialized["status"]
        == "failed"
    )

    assert (
        serialized["error"]
        == "Provider failure."
    )


def test_report_query_result_status_values():

    assert (
        ReportQueryResultStatus.SUCCESS.value
        == "success"
    )

    assert (
        ReportQueryResultStatus.EMPTY.value
        == "empty"
    )

    assert (
        ReportQueryResultStatus.FAILED.value
        == "failed"
    )


def test_report_query_result_preserves_query_identity():

    query = create_query()

    result = ReportQueryResult(
        query=query,
        data=[],
    )

    assert (
        result.query
        is query
    )
