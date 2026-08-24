"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report export execution service contract tests.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.core.reporting import (
    ReportExportFormat,
    ReportExporter,
    ReportExporterRegistry,
    ReportExecutionException,
    ReportExportExecutionService,
    ReportOutputFormat,
    ReportOutputRequest,
    ReportQuery,
    ReportQueryResult,
)


class CSVExporter(ReportExporter):
    """
    Test CSV exporter.
    """

    def __init__(
        self,
    ) -> None:
        self.received_request = None

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
        self.received_request = request

        return {
            "format": "csv",
            "report_code": request.report_code,
        }


class FailingExporter(ReportExporter):
    """
    Test exporter that raises during execution.
    """

    @property
    def name(
        self,
    ) -> str:
        return "failing-test-exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.CSV

    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        raise RuntimeError(
            "Exporter failure."
        )


class IdentityExporter(ReportExporter):
    """
    Test exporter that returns a predefined object.
    """

    def __init__(
        self,
        output: Any,
    ) -> None:
        self.output = output

    @property
    def name(
        self,
    ) -> str:
        return "identity-test-exporter"

    @property
    def format(
        self,
    ) -> ReportExportFormat:
        return ReportExportFormat.CSV

    def export(
        self,
        request: ReportOutputRequest,
    ) -> Any:
        return self.output


def create_query() -> ReportQuery:
    """
    Create a minimal report query for service tests.
    """

    return ReportQuery(
        report_code="TEST-REPORT",
    )


def create_result() -> ReportQueryResult:
    """
    Create a minimal successful report query result.
    """

    return ReportQueryResult(
        query=create_query(),
        data=[
            {
                "id": 1,
                "name": "Test",
            }
        ],
    )


def create_request(
    output_format: ReportOutputFormat = (
        ReportOutputFormat.CSV
    ),
) -> ReportOutputRequest:
    """
    Create a minimal report output request.
    """

    return ReportOutputRequest(
        result=create_result(),
        format=output_format,
        filename="test-report.csv",
        metadata={
            "source": "unit-test",
        },
    )


def create_service(
    exporter: ReportExporter,
) -> ReportExportExecutionService:
    """
    Create an export execution service with a
    supplied test exporter.
    """

    registry = ReportExporterRegistry(
        exporters=[
            exporter,
        ]
    )

    return ReportExportExecutionService(
        exporter_registry=registry,
    )


def test_export_execution_service_requires_registry():

    with pytest.raises(
        ValueError,
        match="ReportExporterRegistry",
    ):
        ReportExportExecutionService(
            exporter_registry=object(),
        )


def test_export_execution_service_rejects_invalid_request():

    service = create_service(
        CSVExporter()
    )

    with pytest.raises(
        ValueError,
        match="Report output request",
    ):
        service.execute(
            object()
        )


def test_export_execution_service_resolves_exporter():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    request = create_request()

    result = service.execute(
        request
    )

    assert (
        exporter.received_request
        is request
    )

    assert result == {
        "format": "csv",
        "report_code": "TEST-REPORT",
    }


def test_export_execution_service_passes_request_to_exporter():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    request = create_request()

    service.execute(
        request
    )

    assert (
        exporter.received_request
        is request
    )


def test_export_execution_service_maps_output_format_to_export_format():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    request = create_request(
        ReportOutputFormat.CSV
    )

    assert (
        ReportExportFormat.normalize(
            request.format.value
        )
        is ReportExportFormat.CSV
    )

    service.execute(
        request
    )

    assert (
        exporter.received_request
        is request
    )


def test_export_execution_service_returns_exporter_output():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    output = service.execute(
        create_request()
    )

    assert output == {
        "format": "csv",
        "report_code": "TEST-REPORT",
    }


def test_export_execution_service_preserves_output_identity():

    expected_output = {
        "rows": [
            {
                "id": 1,
            }
        ]
    }

    service = create_service(
        IdentityExporter(
            expected_output
        )
    )

    result = service.execute(
        create_request()
    )

    assert result is expected_output


def test_export_execution_service_preserves_request_metadata():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    request = create_request()

    service.execute(
        request
    )

    assert (
        exporter.received_request.metadata
        == {
            "source": "unit-test",
        }
    )


def test_export_execution_service_preserves_filename():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    request = create_request()

    service.execute(
        request
    )

    assert (
        exporter.received_request.filename
        == "test-report.csv"
    )


def test_export_execution_service_translates_exporter_failure():

    service = create_service(
        FailingExporter()
    )

    with pytest.raises(
        ReportExecutionException,
        match="Report export execution failed",
    ) as exc_info:

        service.execute(
            create_request()
        )

    assert isinstance(
        exc_info.value.__cause__,
        RuntimeError,
    )


def test_export_execution_service_requires_registered_exporter():

    registry = ReportExporterRegistry()

    service = ReportExportExecutionService(
        exporter_registry=registry
    )

    with pytest.raises(
        ReportExecutionException,
        match="Report export execution failed",
    ):

        service.execute(
            create_request()
        )


def test_export_execution_service_does_not_modify_request():

    exporter = CSVExporter()

    service = create_service(
        exporter
    )

    request = create_request()

    original_metadata = dict(
        request.metadata
    )

    service.execute(
        request
    )

    assert (
        request.metadata
        == original_metadata
    )


def test_export_execution_service_supports_json_output():

    class JSONExporter(
        ReportExporter
    ):
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
            }

    service = create_service(
        JSONExporter()
    )

    request = create_request(
        ReportOutputFormat.JSON
    )

    result = service.execute(
        request
    )

    assert result == {
        "format": "json",
    }


def test_export_execution_service_supports_xlsx_output():

    class XLSXExporter(
        ReportExporter
    ):
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
            }

    service = create_service(
        XLSXExporter()
    )

    request = create_request(
        ReportOutputFormat.XLSX
    )

    result = service.execute(
        request
    )

    assert result == {
        "format": "xlsx",
    }


def test_export_execution_service_supports_pdf_output():

    class PDFExporter(
        ReportExporter
    ):
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
            }

    service = create_service(
        PDFExporter()
    )

    request = create_request(
        ReportOutputFormat.PDF
    )

    result = service.execute(
        request
    )

    assert result == {
        "format": "pdf",
    }
