"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report output and export integration verification tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportExecutionException,
    ReportExportExecutionService,
    ReportExportFormat,
    ReportExporter,
    ReportExporterRegistry,
    ReportOutputFormat,
    ReportOutputRequest,
    ReportQuery,
    ReportQueryResult,
    ReportQueryResultStatus,
)


class StubCSVExporter(ReportExporter):
    """Test exporter for CSV output."""

    @property
    def name(self) -> str:
        return "stub-csv-exporter"

    @property
    def format(self) -> ReportExportFormat:
        return ReportExportFormat.CSV

    def export(
        self,
        request: ReportOutputRequest,
    ) -> dict:
        return {
            "format": request.format.value,
            "report_code": request.report_code,
            "filename": request.filename,
            "metadata": dict(request.metadata),
            "data": request.result.data,
        }


class StubJSONExporter(ReportExporter):
    """Test exporter for JSON output."""

    @property
    def name(self) -> str:
        return "stub-json-exporter"

    @property
    def format(self) -> ReportExportFormat:
        return ReportExportFormat.JSON

    def export(
        self,
        request: ReportOutputRequest,
    ) -> dict:
        return {
            "format": request.format.value,
            "report_code": request.report_code,
            "filename": request.filename,
            "metadata": dict(request.metadata),
            "data": request.result.data,
        }


class FailingCSVExporter(ReportExporter):
    """Test exporter that deliberately fails."""

    @property
    def name(self) -> str:
        return "failing-csv-exporter"

    @property
    def format(self) -> ReportExportFormat:
        return ReportExportFormat.CSV

    def export(
        self,
        request: ReportOutputRequest,
    ) -> dict:
        raise RuntimeError(
            "Simulated exporter failure."
        )


def _build_result() -> ReportQueryResult:
    """Create a representative successful report result."""

    query = ReportQuery(
        report_code="sales_summary",
        metadata={
            "domain": "sales",
        },
    )

    return ReportQueryResult(
        query=query,
        data=[
            {
                "id": 1,
                "amount": 1250,
            },
            {
                "id": 2,
                "amount": 2750,
            },
        ],
        status=ReportQueryResultStatus.SUCCESS,
        metadata={
            "row_count": 2,
        },
    )


def _build_csv_request() -> ReportOutputRequest:
    """Create a representative CSV output request."""

    return ReportOutputRequest(
        result=_build_result(),
        format=ReportOutputFormat.CSV,
        filename="sales-summary.csv",
        metadata={
            "requested_by": "integration-test",
            "department": "finance",
        },
    )


def _build_service(
    exporter: ReportExporter,
) -> ReportExportExecutionService:
    """Create an export execution service."""

    registry = ReportExporterRegistry(
        exporters=[
            exporter,
        ]
    )

    return ReportExportExecutionService(
        exporter_registry=registry,
    )


def test_output_request_integrates_with_export_format():

    request = _build_csv_request()

    assert (
        ReportExportFormat.normalize(
            request.format.value
        )
        is ReportExportFormat.CSV
    )


def test_output_request_integrates_with_exporter_registry():

    exporter = StubCSVExporter()

    registry = ReportExporterRegistry(
        exporters=[
            exporter,
        ]
    )

    request = _build_csv_request()

    resolved = registry.resolve(
        request.format
    )

    assert resolved is exporter


def test_output_request_integrates_with_export_execution_service():

    exporter = StubCSVExporter()

    service = _build_service(
        exporter
    )

    request = _build_csv_request()

    output = service.execute(
        request
    )

    assert output["format"] == "csv"
    assert output["report_code"] == "sales_summary"
    assert output["filename"] == "sales-summary.csv"


def test_export_execution_service_preserves_result_data():

    exporter = StubCSVExporter()

    service = _build_service(
        exporter
    )

    request = _build_csv_request()

    output = service.execute(
        request
    )

    assert output["data"] == [
        {
            "id": 1,
            "amount": 1250,
        },
        {
            "id": 2,
            "amount": 2750,
        },
    ]


def test_export_execution_service_preserves_output_metadata():

    exporter = StubCSVExporter()

    service = _build_service(
        exporter
    )

    request = _build_csv_request()

    output = service.execute(
        request
    )

    assert output["metadata"] == {
        "requested_by": "integration-test",
        "department": "finance",
    }


def test_export_execution_service_does_not_modify_request():

    exporter = StubCSVExporter()

    service = _build_service(
        exporter
    )

    request = _build_csv_request()

    original_format = request.format
    original_filename = request.filename
    original_metadata = dict(
        request.metadata
    )

    service.execute(
        request
    )

    assert request.format is original_format
    assert request.filename == original_filename
    assert request.metadata == original_metadata


def test_export_execution_service_supports_multiple_formats():

    csv_exporter = StubCSVExporter()
    json_exporter = StubJSONExporter()

    registry = ReportExporterRegistry(
        exporters=[
            csv_exporter,
            json_exporter,
        ]
    )

    service = ReportExportExecutionService(
        exporter_registry=registry,
    )

    result = _build_result()

    csv_request = ReportOutputRequest(
        result=result,
        format=ReportOutputFormat.CSV,
        filename="sales.csv",
    )

    json_request = ReportOutputRequest(
        result=result,
        format=ReportOutputFormat.JSON,
        filename="sales.json",
    )

    csv_output = service.execute(
        csv_request
    )

    json_output = service.execute(
        json_request
    )

    assert csv_output["format"] == "csv"
    assert json_output["format"] == "json"

    assert (
        csv_output["report_code"]
        == json_output["report_code"]
        == "sales_summary"
    )


def test_export_execution_service_preserves_exporter_output_identity():

    expected_output = {
        "generated": True,
        "format": "csv",
        "records": 2,
    }

    class IdentityCSVExporter(ReportExporter):

        @property
        def name(self) -> str:
            return "identity-csv-exporter"

        @property
        def format(self) -> ReportExportFormat:
            return ReportExportFormat.CSV

        def export(
            self,
            request: ReportOutputRequest,
        ) -> dict:
            return expected_output

    service = _build_service(
        IdentityCSVExporter()
    )

    output = service.execute(
        _build_csv_request()
    )

    assert output is expected_output


def test_export_execution_service_translates_exporter_failure():

    service = _build_service(
        FailingCSVExporter()
    )

    with pytest.raises(
        ReportExecutionException,
        match="Report export execution failed",
    ):
        service.execute(
            _build_csv_request()
        )


def test_export_execution_service_requires_registered_exporter():

    registry = ReportExporterRegistry()

    service = ReportExportExecutionService(
        exporter_registry=registry,
    )

    request = _build_csv_request()

    with pytest.raises(
        ReportExecutionException,
    ):
        service.execute(
            request
        )


def test_export_execution_service_rejects_invalid_request():

    service = _build_service(
        StubCSVExporter()
    )

    with pytest.raises(
        ValueError,
        match="Report output request",
    ):
        service.execute(
            None
        )
