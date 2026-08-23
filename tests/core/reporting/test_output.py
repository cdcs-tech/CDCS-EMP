"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report output contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportOutputFormat,
    ReportOutputRequest,
    ReportQuery,
    ReportQueryResult,
    ReportQueryResultStatus,
)


def create_result() -> ReportQueryResult:
    """
    Create a standard report query result.
    """

    query = ReportQuery(
        report_code="EXAMPLE",
        metadata={
            "source": "test",
        },
    )

    return ReportQueryResult(
        query=query,
        data={
            "rows": [
                {
                    "id": 1,
                    "name": "Example",
                }
            ],
        },
        status=ReportQueryResultStatus.SUCCESS,
        metadata={
            "provider": "example",
        },
    )


def test_report_output_format_contains_supported_formats():

    assert (
        ReportOutputFormat.JSON.value
        == "json"
    )

    assert (
        ReportOutputFormat.CSV.value
        == "csv"
    )

    assert (
        ReportOutputFormat.XLSX.value
        == "xlsx"
    )

    assert (
        ReportOutputFormat.PDF.value
        == "pdf"
    )


def test_report_output_format_is_string_enum():

    assert isinstance(
        ReportOutputFormat.JSON,
        str,
    )

    assert (
        str(ReportOutputFormat.JSON)
        == "ReportOutputFormat.JSON"
    )


def test_report_output_request_accepts_result_and_format():

    result = create_result()

    request = ReportOutputRequest(
        result=result,
        format=ReportOutputFormat.JSON,
    )

    assert (
        request.result
        is result
    )

    assert (
        request.format
        == ReportOutputFormat.JSON
    )


def test_report_output_request_accepts_string_format():

    request = ReportOutputRequest(
        result=create_result(),
        format="json",
    )

    assert (
        request.format
        == ReportOutputFormat.JSON
    )


@pytest.mark.parametrize(
    "output_format",
    [
        "JSON",
        " json ",
        "CSV",
        " csv ",
        "XLSX",
        "PDF",
    ],
)
def test_report_output_request_normalizes_string_format(
    output_format,
):

    request = ReportOutputRequest(
        result=create_result(),
        format=output_format,
    )

    assert isinstance(
        request.format,
        ReportOutputFormat,
    )

    assert (
        request.format.value
        == output_format.strip().lower()
    )


def test_report_output_request_rejects_invalid_result():

    with pytest.raises(
        ValueError,
        match="Report output result",
    ):
        ReportOutputRequest(
            result=object(),
            format=ReportOutputFormat.JSON,
        )


def test_report_output_request_rejects_invalid_format():

    with pytest.raises(
        ValueError,
        match="Report output format",
    ):
        ReportOutputRequest(
            result=create_result(),
            format=object(),
        )


def test_report_output_request_rejects_invalid_string_format():

    with pytest.raises(
        ValueError,
        match="Invalid report output format",
    ):
        ReportOutputRequest(
            result=create_result(),
            format="xml",
        )


def test_report_output_request_accepts_optional_filename():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.CSV,
        filename="financial-report.csv",
    )

    assert (
        request.filename
        == "financial-report.csv"
    )


def test_report_output_request_normalizes_filename():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.CSV,
        filename="  financial-report.csv  ",
    )

    assert (
        request.filename
        == "financial-report.csv"
    )


def test_report_output_request_accepts_no_filename():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.JSON,
    )

    assert (
        request.filename
        is None
    )


def test_report_output_request_rejects_invalid_filename_type():

    with pytest.raises(
        ValueError,
        match="Report output filename",
    ):
        ReportOutputRequest(
            result=create_result(),
            format=ReportOutputFormat.JSON,
            filename=123,
        )


def test_report_output_request_rejects_blank_filename():

    with pytest.raises(
        ValueError,
        match="Report output filename",
    ):
        ReportOutputRequest(
            result=create_result(),
            format=ReportOutputFormat.JSON,
            filename="   ",
        )


def test_report_output_request_accepts_metadata():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.JSON,
        metadata={
            "requested_by": "user-001",
            "source": "web",
        },
    )

    assert (
        request.metadata
        == {
            "requested_by": "user-001",
            "source": "web",
        }
    )


def test_report_output_request_copies_metadata_boundary():

    metadata = {
        "source": "web",
    }

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.JSON,
        metadata=metadata,
    )

    metadata["changed"] = True

    assert (
        request.metadata
        == {
            "source": "web",
        }
    )


def test_report_output_request_rejects_invalid_metadata():

    with pytest.raises(
        ValueError,
        match="Report output metadata",
    ):
        ReportOutputRequest(
            result=create_result(),
            format=ReportOutputFormat.JSON,
            metadata=[],
        )


def test_report_output_request_exposes_report_code():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.JSON,
    )

    assert (
        request.report_code
        == "EXAMPLE"
    )


def test_report_output_request_exposes_identifier():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.JSON,
    )

    assert (
        request.identifier
        == request.result.query.identifier
    )


def test_report_output_request_to_dict():

    result = create_result()

    request = ReportOutputRequest(
        result=result,
        format=ReportOutputFormat.XLSX,
        filename="example.xlsx",
        metadata={
            "requested_by": "user-001",
        },
    )

    serialized = request.to_dict()

    assert (
        serialized["result"]
        == result.to_dict()
    )

    assert (
        serialized["format"]
        == "xlsx"
    )

    assert (
        serialized["filename"]
        == "example.xlsx"
    )

    assert (
        serialized["metadata"]
        == {
            "requested_by": "user-001",
        }
    )


def test_report_output_request_is_immutable():

    request = ReportOutputRequest(
        result=create_result(),
        format=ReportOutputFormat.JSON,
    )

    with pytest.raises(
        AttributeError,
    ):
        request.filename = "changed.json"


def test_report_output_request_does_not_modify_query_result():

    result = create_result()

    original_data = result.data

    ReportOutputRequest(
        result=result,
        format=ReportOutputFormat.JSON,
        metadata={
            "source": "test",
        },
    )

    assert (
        result.data
        is original_data
    )


def test_public_output_format_is_available():

    from app.core.reporting import (
        ReportOutputFormat as PublicOutputFormat,
    )

    assert (
        PublicOutputFormat
        is ReportOutputFormat
    )


def test_public_output_request_is_available():

    from app.core.reporting import (
        ReportOutputRequest as PublicOutputRequest,
    )

    assert (
        PublicOutputRequest
        is ReportOutputRequest
    )
