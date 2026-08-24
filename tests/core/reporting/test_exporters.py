"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report exporter contract tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.core.reporting import (
    ReportExportFormat,
    ReportExporter,
)


class CsvTestExporter(
    ReportExporter,
):
    """
    Minimal concrete exporter used exclusively for
    testing the provider-neutral exporter contract.
    """

    @property
    def name(
        self,
    ) -> str:
        return "csv_test_exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.CSV

    def export(
        self,
        request,
    ) -> Any:
        return {
            "format": self.format.value,
            "request": request,
        }


class JsonTestExporter(
    ReportExporter,
):
    """
    Minimal JSON exporter used for format capability tests.
    """

    @property
    def name(
        self,
    ) -> str:
        return "json_test_exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.JSON

    def export(
        self,
        request,
    ) -> Any:
        return {
            "format": self.format.value,
            "request": request,
        }


def test_report_exporter_is_abstract():

    assert ReportExporter.__abstractmethods__ == {
        "name",
        "format",
        "export",
    }


def test_report_exporter_cannot_be_instantiated():

    with pytest.raises(
        TypeError,
    ):
        ReportExporter()


def test_concrete_exporter_exposes_name():

    exporter = CsvTestExporter()

    assert (
        exporter.name
        == "csv_test_exporter"
    )


def test_concrete_exporter_exposes_format():

    exporter = CsvTestExporter()

    assert (
        exporter.format
        is ReportExportFormat.CSV
    )


@pytest.mark.parametrize(
    "value",
    [
        ReportExportFormat.CSV,
        "csv",
        "CSV",
        " csv ",
    ],
)
def test_exporter_supports_its_format(
    value,
):

    exporter = CsvTestExporter()

    assert (
        exporter.supports(
            value
        )
        is True
    )


@pytest.mark.parametrize(
    "value",
    [
        ReportExportFormat.XLSX,
        ReportExportFormat.PDF,
        ReportExportFormat.JSON,
        "xlsx",
        "pdf",
        "json",
    ],
)
def test_exporter_rejects_unsupported_format(
    value,
):

    exporter = CsvTestExporter()

    assert (
        exporter.supports(
            value
        )
        is False
    )


def test_json_exporter_supports_json():

    exporter = JsonTestExporter()

    assert (
        exporter.supports(
            ReportExportFormat.JSON
        )
        is True
    )


def test_json_exporter_rejects_csv():

    exporter = JsonTestExporter()

    assert (
        exporter.supports(
            ReportExportFormat.CSV
        )
        is False
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
def test_exporter_supports_rejects_invalid_format(
    value,
):

    exporter = CsvTestExporter()

    with pytest.raises(
        ValueError,
        match="Report export format",
    ):
        exporter.supports(
            value
        )


def test_exporter_export_operation_is_available():

    exporter = CsvTestExporter()

    request = object()

    result = exporter.export(
        request
    )

    assert (
        result["format"]
        == "csv"
    )

    assert (
        result["request"]
        is request
    )


def test_exporter_export_preserves_request_identity():

    exporter = CsvTestExporter()

    request = object()

    result = exporter.export(
        request
    )

    assert (
        result["request"]
        is request
    )


def test_exporter_contract_allows_different_formats():

    csv_exporter = CsvTestExporter()
    json_exporter = JsonTestExporter()

    assert (
        csv_exporter.format
        is not json_exporter.format
    )

    assert (
        csv_exporter.supports(
            ReportExportFormat.CSV
        )
        is True
    )

    assert (
        json_exporter.supports(
            ReportExportFormat.JSON
        )
        is True
    )


def test_exporter_contract_requires_name():

    class MissingNameExporter(
        ReportExporter,
    ):
        @property
        def format(
            self,
        ) -> ReportExportFormat:
            return ReportExportFormat.CSV

        def export(
            self,
            request,
        ) -> Any:
            return request

    with pytest.raises(
        TypeError,
    ):
        MissingNameExporter()


def test_exporter_contract_requires_format():

    class MissingFormatExporter(
        ReportExporter,
    ):
        @property
        def name(
            self,
        ) -> str:
            return "missing_format"

        def export(
            self,
            request,
        ) -> Any:
            return request

    with pytest.raises(
        TypeError,
    ):
        MissingFormatExporter()


def test_exporter_contract_requires_export():

    class MissingExportExporter(
        ReportExporter,
    ):
        @property
        def name(
            self,
        ) -> str:
            return "missing_export"

        @property
        def format(
            self,
        ) -> ReportExportFormat:
            return ReportExportFormat.CSV

    with pytest.raises(
        TypeError,
    ):
        MissingExportExporter()


def test_public_report_exporter_is_available():

    from app.core.reporting import (
        ReportExporter as PublicReportExporter,
    )

    assert (
        PublicReportExporter
        is ReportExporter
    )
