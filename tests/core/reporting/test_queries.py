"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report query contract tests.
"""

import pytest

from app.core.reporting import (
    ReportQuery,
)


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
