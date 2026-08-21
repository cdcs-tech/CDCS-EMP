"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report result contract tests.
"""

from app.core.reporting import (
    ReportDefinition,
    ReportResult,
    ReportResultStatus,
)


def create_definition():
    return ReportDefinition(
        code="EXAMPLE",
        name="Example Report",
        description="Example reporting definition.",
    )


def test_report_result_defaults():

    definition = create_definition()

    result = ReportResult(
        definition=definition,
    )

    assert (
        result.definition
        is definition
    )

    assert (
        result.data
        is None
    )

    assert (
        result.status
        == ReportResultStatus.SUCCESS
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


def test_report_result_success_state():

    result = ReportResult(
        definition=create_definition(),
        data=[
            {
                "id": 1,
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


def test_report_result_empty_state():

    result = ReportResult(
        definition=create_definition(),
        status=ReportResultStatus.EMPTY,
        data=[],
        message="No report data was found.",
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
        == "No report data was found."
    )


def test_report_result_failed_state():

    result = ReportResult(
        definition=create_definition(),
        status=ReportResultStatus.FAILED,
        error="Report generation failed.",
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
        == "Report generation failed."
    )


def test_report_result_metadata_is_independent():

    metadata = {
        "provider": "example",
        "execution_id": "123",
    }

    result = ReportResult(
        definition=create_definition(),
        metadata=metadata,
    )

    metadata["provider"] = "changed"

    assert (
        result.metadata["provider"]
        == "changed"
    )


def test_report_result_to_dict():

    definition = create_definition()

    result = ReportResult(
        definition=definition,
        data={
            "total": 25,
        },
        status=ReportResultStatus.SUCCESS,
        metadata={
            "provider": "example",
        },
        message="Report generated.",
    )

    serialized = result.to_dict()

    assert (
        serialized["definition"]
        == definition.to_dict()
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
        == "example"
    )

    assert (
        serialized["message"]
        == "Report generated."
    )

    assert (
        serialized["error"]
        is None
    )


def test_report_result_failed_to_dict():

    result = ReportResult(
        definition=create_definition(),
        status=ReportResultStatus.FAILED,
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


def test_report_result_status_values():

    assert (
        ReportResultStatus.SUCCESS.value
        == "success"
    )

    assert (
        ReportResultStatus.EMPTY.value
        == "empty"
    )

    assert (
        ReportResultStatus.FAILED.value
        == "failed"
    )
