"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report query contract tests.
"""

import pytest

from app.core.reporting import (
    ReportQuery,
)

from app.core.data import QueryOptions

def test_report_query_creation():

    query = ReportQuery(
        report_code="FINANCE_MONTHLY",
    )

    assert (
        query.report_code
        == "FINANCE_MONTHLY"
    )

    assert (
        query.metadata
        == {}
    )


def test_report_query_report_code_is_normalized():

    query = ReportQuery(
        report_code="  finance_monthly  ",
    )

    assert (
        query.report_code
        == "finance_monthly"
    )


def test_report_query_identifier_is_canonical():

    query = ReportQuery(
        report_code="finance_monthly",
    )

    assert (
        query.identifier
        == "FINANCE_MONTHLY"
    )


def test_report_query_metadata_is_supported():

    query = ReportQuery(
        report_code="FINANCE_MONTHLY",
        metadata={
            "source": "finance",
            "context": "monthly",
        },
    )

    assert (
        query.metadata
        == {
            "source": "finance",
            "context": "monthly",
        }
    )


def test_report_query_metadata_is_copied():

    metadata = {
        "source": "finance",
    }

    query = ReportQuery(
        report_code="FINANCE_MONTHLY",
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert (
        query.metadata["source"]
        == "finance"
    )


def test_report_query_requires_string_report_code():

    with pytest.raises(ValueError):

        ReportQuery(
            report_code=123,
        )


def test_report_query_requires_report_code():

    with pytest.raises(ValueError):

        ReportQuery(
            report_code="",
        )


def test_report_query_rejects_blank_report_code():

    with pytest.raises(ValueError):

        ReportQuery(
            report_code="   ",
        )


def test_report_query_is_immutable():

    query = ReportQuery(
        report_code="FINANCE_MONTHLY",
    )

    with pytest.raises(
        AttributeError
    ):

        query.report_code = "OTHER"


def test_report_query_to_dict():

    query = ReportQuery(
        report_code="FINANCE_MONTHLY",
        metadata={
            "source": "finance",
        },
    )

    result = query.to_dict()

    assert result == {
        "report_code": "FINANCE_MONTHLY",
        "metadata": {
            "source": "finance",
        },
    }


def test_public_report_query_is_available():

    from app.core.reporting import (
        ReportQuery as PublicReportQuery,
    )

    assert (
        PublicReportQuery
        is ReportQuery
    )

def test_report_query_accepts_query_options():

    query_options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
        filters={
            "status": "active",
        },
        search="finance",
        fields=[
            "id",
            "name",
        ],
    )

    query = ReportQuery(
        report_code="FINANCE.REVENUE",
        query_options=query_options,
    )

    assert query.query_options is query_options

def test_report_query_rejects_invalid_query_options():

    try:
        ReportQuery(
            report_code="FINANCE.REVENUE",
            query_options="invalid",
        )
    except ValueError as exc:
        assert (
            str(exc)
            == (
                "Report query query_options must be "
                "a QueryOptions instance or None."
            )
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )

def test_report_query_serializes_query_options():

    query_options = QueryOptions(
        page=2,
        page_size=50,
        sort_by="name",
        sort_direction="desc",
        filters={
            "status": "active",
        },
    )

    query = ReportQuery(
        report_code="FINANCE.REVENUE",
        metadata={
            "source": "finance",
        },
        query_options=query_options,
    )

    serialized = query.to_dict()

    assert serialized["report_code"] == (
        "FINANCE.REVENUE"
    )

    assert serialized["metadata"] == {
        "source": "finance",
    }

    assert serialized["query_options"] == {
        "page": 2,
        "page_size": 50,
        "sort_by": "name",
        "sort_direction": "desc",
        "filters": {
            "status": "active",
        },
        "search": None,
        "fields": [],
        "include_inactive": False,
    }

def test_report_query_without_query_options_remains_valid():

    query = ReportQuery(
        report_code="FINANCE.REVENUE",
    )

    assert query.query_options is None

    assert "query_options" not in query.to_dict()
