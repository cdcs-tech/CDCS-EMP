"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report exporter registry contract tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.core.reporting import (
    ReportExportFormat,
    ReportExporter,
    ReportExporterRegistry,
    ReportOutputRequest,
)


class CSVExporter(ReportExporter):
    """
    Test exporter implementation for CSV.
    """

    @property
    def name(
        self,
    ) -> str:
        return "csv-test-exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.CSV

    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        return {
            "format": "csv",
            "request": request,
        }


class XLSXExporter(ReportExporter):
    """
    Test exporter implementation for XLSX.
    """

    @property
    def name(
        self,
    ) -> str:
        return "xlsx-test-exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.XLSX

    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        return {
            "format": "xlsx",
            "request": request,
        }


class PDFExporter(ReportExporter):
    """
    Test exporter implementation for PDF.
    """

    @property
    def name(
        self,
    ) -> str:
        return "pdf-test-exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.PDF

    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        return {
            "format": "pdf",
            "request": request,
        }


class JSONExporter(ReportExporter):
    """
    Test exporter implementation for JSON.
    """

    @property
    def name(
        self,
    ) -> str:
        return "json-test-exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.JSON

    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        return {
            "format": "json",
            "request": request,
        }


class InvalidExporter:
    """
    Test object that does not implement ReportExporter.
    """

    format = ReportExportFormat.CSV


def test_exporter_registry_can_be_created_empty():

    registry = ReportExporterRegistry()

    assert registry.all() == ()


def test_exporter_registry_registers_exporter():

    exporter = CSVExporter()

    registry = ReportExporterRegistry()

    registry.register(
        exporter
    )

    assert registry.get(
        ReportExportFormat.CSV
    ) is exporter


def test_exporter_registry_resolves_registered_exporter():

    exporter = CSVExporter()

    registry = ReportExporterRegistry(
        exporters=[
            exporter
        ]
    )

    assert registry.resolve(
        ReportExportFormat.CSV
    ) is exporter


@pytest.mark.parametrize(
    "value",
    [
        "csv",
        "CSV",
        " csv ",
    ],
)
def test_exporter_registry_normalizes_format(
    value,
):

    exporter = CSVExporter()

    registry = ReportExporterRegistry(
        exporters=[
            exporter
        ]
    )

    assert registry.get(
        value
    ) is exporter


def test_exporter_registry_accepts_initial_exporters():

    csv_exporter = CSVExporter()
    xlsx_exporter = XLSXExporter()

    registry = ReportExporterRegistry(
        exporters=[
            csv_exporter,
            xlsx_exporter,
        ]
    )

    assert registry.get(
        ReportExportFormat.CSV
    ) is csv_exporter

    assert registry.get(
        ReportExportFormat.XLSX
    ) is xlsx_exporter


def test_exporter_registry_rejects_invalid_exporter():

    registry = ReportExporterRegistry()

    with pytest.raises(
        Exception,
        match="Exporter must implement ReportExporter",
    ):
        registry.register(
            InvalidExporter()
        )


def test_exporter_registry_rejects_duplicate_format():

    registry = ReportExporterRegistry()

    registry.register(
        CSVExporter()
    )

    with pytest.raises(
        Exception,
        match="already registered",
    ):
        registry.register(
            CSVExporter()
        )


def test_exporter_registry_has_registered_format():

    registry = ReportExporterRegistry()

    registry.register(
        CSVExporter()
    )

    assert registry.has(
        ReportExportFormat.CSV
    ) is True

    assert registry.has(
        ReportExportFormat.XLSX
    ) is False


def test_exporter_registry_get_raises_for_missing_format():

    registry = ReportExporterRegistry()

    with pytest.raises(
        KeyError
    ):
        registry.get(
            ReportExportFormat.CSV
        )


def test_exporter_registry_resolve_raises_for_missing_format():

    registry = ReportExporterRegistry()

    with pytest.raises(
        KeyError
    ):
        registry.resolve(
            ReportExportFormat.CSV
        )


def test_exporter_registry_unregisters_exporter():

    exporter = CSVExporter()

    registry = ReportExporterRegistry(
        exporters=[
            exporter
        ]
    )

    registry.unregister(
        ReportExportFormat.CSV
    )

    assert registry.has(
        ReportExportFormat.CSV
    ) is False

    assert registry.all() == ()


def test_exporter_registry_unregister_raises_for_missing_format():

    registry = ReportExporterRegistry()

    with pytest.raises(
        KeyError
    ):
        registry.unregister(
            ReportExportFormat.CSV
        )


def test_exporter_registry_all_preserves_registration_order():

    csv_exporter = CSVExporter()
    xlsx_exporter = XLSXExporter()
    pdf_exporter = PDFExporter()
    json_exporter = JSONExporter()

    registry = ReportExporterRegistry(
        exporters=[
            csv_exporter,
            xlsx_exporter,
            pdf_exporter,
            json_exporter,
        ]
    )

    assert registry.all() == (
        csv_exporter,
        xlsx_exporter,
        pdf_exporter,
        json_exporter,
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
def test_exporter_registry_rejects_invalid_format(
    value,
):

    registry = ReportExporterRegistry()

    with pytest.raises(
        ValueError,
        match="Invalid report export format",
    ):
        registry.has(
            value
        )


def test_exporter_registry_get_rejects_invalid_format():

    registry = ReportExporterRegistry()

    with pytest.raises(
        ValueError,
        match="Invalid report export format",
    ):
        registry.get(
            "xml"
        )


def test_exporter_registry_resolve_rejects_invalid_format():

    registry = ReportExporterRegistry()

    with pytest.raises(
        ValueError,
        match="Invalid report export format",
    ):
        registry.resolve(
            "xml"
        )


def test_exporter_registry_unregister_rejects_invalid_format():

    registry = ReportExporterRegistry()

    with pytest.raises(
        ValueError,
        match="Invalid report export format",
    ):
        registry.unregister(
            "xml"
        )


def test_exporter_registry_can_register_all_supported_formats():

    exporters = [
        CSVExporter(),
        XLSXExporter(),
        PDFExporter(),
        JSONExporter(),
    ]

    registry = ReportExporterRegistry()

    for exporter in exporters:

        registry.register(
            exporter
        )

    assert registry.all() == tuple(
        exporters
    )


def test_public_report_exporter_registry_is_available():

    from app.core.reporting import (
        ReportExporterRegistry as PublicReportExporterRegistry,
    )

    assert (
        PublicReportExporterRegistry
        is ReportExporterRegistry
    )
