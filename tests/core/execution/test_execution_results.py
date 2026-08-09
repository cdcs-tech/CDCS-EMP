"""
Execution result integration tests.
"""

import pytest

from app.core.execution import (
    ExecutionResult,
    ExecutionResultException,
    enrich_execution_result,
    normalize_execution_result,
)


def test_success_result_is_valid():

    result = (
        ExecutionResult.success_result(
            data={
                "id": 1,
            },
            message="Operation completed.",
        )
    )

    assert result.is_success()
    assert not result.is_failure()
    assert result.data["id"] == 1
    assert (
        result.message
        == "Operation completed."
    )


def test_failure_result_is_valid():

    result = (
        ExecutionResult.failure_result(
            "Operation failed.",
            error_code="TEST_ERROR",
        )
    )

    assert result.is_failure()
    assert not result.is_success()
    assert (
        result.error_code
        == "TEST_ERROR"
    )


def test_result_metadata_can_be_enriched():

    result = (
        ExecutionResult.success_result(
            data="value"
        )
    )

    enriched = (
        result.with_metadata(
            request_id="REQ-001"
        )
    )

    assert (
        "request_id"
        not in result.metadata
    )

    assert (
        enriched.metadata[
            "request_id"
        ]
        == "REQ-001"
    )


def test_result_validation_rejects_invalid_success():

    result = ExecutionResult(
        success=True,
        error_code="INVALID",
    )

    with pytest.raises(
        ExecutionResultException
    ):

        result.validate()


def test_result_validation_rejects_invalid_error_code():

    result = ExecutionResult(
        success=False,
        error_code="",
    )

    with pytest.raises(
        ExecutionResultException
    ):

        result.validate()


def test_normalize_execution_result():

    result = (
        ExecutionResult.success_result(
            data="normalized"
        )
    )

    normalized = (
        normalize_execution_result(
            result
        )
    )

    assert (
        normalized is result
    )


def test_enrich_execution_result():

    result = (
        ExecutionResult.success_result(
            data="value"
        )
    )

    enriched = (
        enrich_execution_result(
            result,
            command="test.command",
            module_name="test",
        )
    )

    assert (
        enriched.metadata[
            "command"
        ]
        == "test.command"
    )

    assert (
        enriched.metadata[
            "module_name"
        ]
        == "test"
    )


def test_invalid_result_is_rejected():

    with pytest.raises(
        Exception
    ):

        normalize_execution_result(
            "not-a-result"
        )
