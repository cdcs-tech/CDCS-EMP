"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report export format contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportExportFormat,
)


def test_report_export_format_is_string_enum():

    assert issubclass(
        ReportExportFormat,
        str,
    )


def test_report_export_format_defines_csv():

    assert (
        ReportExportFormat.CSV.value
        == "csv"
    )


def test_report_export_format_defines_xlsx():

    assert (
        ReportExportFormat.XLSX.value
        == "xlsx"
    )


def test_report_export_format_defines_pdf():

    assert (
        ReportExportFormat.PDF.value
        == "pdf"
    )


def test_report_export_format_defines_json():

    assert (
        ReportExportFormat.JSON.value
        == "json"
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (
            "csv",
            ReportExportFormat.CSV,
        ),
        (
            "CSV",
            ReportExportFormat.CSV,
        ),
        (
            " csv ",
            ReportExportFormat.CSV,
        ),
        (
            "xlsx",
            ReportExportFormat.XLSX,
        ),
        (
            "XLSX",
            ReportExportFormat.XLSX,
        ),
        (
            " xlsx ",
            ReportExportFormat.XLSX,
        ),
        (
            "pdf",
            ReportExportFormat.PDF,
        ),
        (
            "PDF",
            ReportExportFormat.PDF,
        ),
        (
            " pdf ",
            ReportExportFormat.PDF,
        ),
        (
            "json",
            ReportExportFormat.JSON,
        ),
        (
            "JSON",
            ReportExportFormat.JSON,
        ),
        (
            " json ",
            ReportExportFormat.JSON,
        ),
    ],
)
def test_report_export_format_normalizes_string(
    value,
    expected,
):

    assert (
        ReportExportFormat.normalize(
            value
        )
        is expected
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "xml",
        "docx",
        "html",
        "unknown",
        None,
        123,
        object(),
    ],
)
def test_report_export_format_rejects_unsupported_values(
    value,
):

    with pytest.raises(
        ValueError,
        match="Report export format",
    ):
        ReportExportFormat.normalize(
            value
        )


def test_report_export_format_normalize_preserves_enum():

    format_value = ReportExportFormat.CSV

    assert (
        ReportExportFormat.normalize(
            format_value
        )
        is format_value
    )


def test_report_export_format_code():

    assert (
        ReportExportFormat.CSV.code
        == "csv"
    )

    assert (
        ReportExportFormat.XLSX.code
        == "xlsx"
    )

    assert (
        ReportExportFormat.PDF.code
        == "pdf"
    )

    assert (
        ReportExportFormat.JSON.code
        == "json"
    )


def test_report_export_format_labels():

    assert (
        ReportExportFormat.CSV.label
        == "CSV"
    )

    assert (
        ReportExportFormat.XLSX.label
        == "Excel"
    )

    assert (
        ReportExportFormat.PDF.label
        == "PDF"
    )

    assert (
        ReportExportFormat.JSON.label
        == "JSON"
    )


def test_report_export_format_to_dict():

    assert (
        ReportExportFormat.CSV.to_dict()
        == {
            "code": "csv",
            "label": "CSV",
        }
    )


def test_report_export_format_to_dict_for_xlsx():

    assert (
        ReportExportFormat.XLSX.to_dict()
        == {
            "code": "xlsx",
            "label": "Excel",
        }
    )


def test_report_export_format_to_dict_for_pdf():

    assert (
        ReportExportFormat.PDF.to_dict()
        == {
            "code": "pdf",
            "label": "PDF",
        }
    )


def test_report_export_format_to_dict_for_json():

    assert (
        ReportExportFormat.JSON.to_dict()
        == {
            "code": "json",
            "label": "JSON",
        }
    )


def test_report_export_format_members_are_unique():

    values = [
        format_value.value
        for format_value
        in ReportExportFormat
    ]

    assert len(values) == len(
        set(values)
    )


def test_report_export_format_iteration_order():

    assert list(
        ReportExportFormat
    ) == [
        ReportExportFormat.CSV,
        ReportExportFormat.XLSX,
        ReportExportFormat.PDF,
        ReportExportFormat.JSON,
    ]


def test_public_report_export_format_is_available():

    from app.core.reporting import (
        ReportExportFormat as PublicReportExportFormat,
    )

    assert (
        PublicReportExportFormat
        is ReportExportFormat
    )
