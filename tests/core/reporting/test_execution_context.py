"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework Tests

Report execution context contract tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting import (
    ReportExecutionContext,
)


def test_execution_context_defaults():

    context = ReportExecutionContext()

    assert (
        context.correlation_id
        is None
    )

    assert (
        context.requested_by
        is None
    )

    assert (
        context.source
        is None
    )

    assert (
        context.metadata
        == {}
    )


def test_execution_context_accepts_execution_metadata():

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="web",
        metadata={
            "channel": "portal",
            "environment": "test",
        },
    )

    assert (
        context.correlation_id
        == "corr-001"
    )

    assert (
        context.requested_by
        == "user-001"
    )

    assert (
        context.source
        == "web"
    )

    assert (
        context.metadata["channel"]
        == "portal"
    )

    assert (
        context.metadata["environment"]
        == "test"
    )


def test_execution_context_normalizes_string_values():

    context = ReportExecutionContext(
        correlation_id="  corr-001  ",
        requested_by="  user-001  ",
        source="  web  ",
    )

    assert (
        context.correlation_id
        == "corr-001"
    )

    assert (
        context.requested_by
        == "user-001"
    )

    assert (
        context.source
        == "web"
    )


def test_execution_context_rejects_invalid_correlation_id():

    with pytest.raises(
        ValueError,
        match="correlation_id",
    ):

        ReportExecutionContext(
            correlation_id=123,
        )


def test_execution_context_rejects_empty_correlation_id():

    with pytest.raises(
        ValueError,
        match="correlation_id",
    ):

        ReportExecutionContext(
            correlation_id="   ",
        )


def test_execution_context_rejects_invalid_requested_by():

    with pytest.raises(
        ValueError,
        match="requested_by",
    ):

        ReportExecutionContext(
            requested_by=123,
        )


def test_execution_context_rejects_empty_requested_by():

    with pytest.raises(
        ValueError,
        match="requested_by",
    ):

        ReportExecutionContext(
            requested_by="   ",
        )


def test_execution_context_rejects_invalid_source():

    with pytest.raises(
        ValueError,
        match="source",
    ):

        ReportExecutionContext(
            source=123,
        )


def test_execution_context_rejects_empty_source():

    with pytest.raises(
        ValueError,
        match="source",
    ):

        ReportExecutionContext(
            source="   ",
        )


def test_execution_context_rejects_invalid_metadata():

    with pytest.raises(
        ValueError,
        match="metadata",
    ):

        ReportExecutionContext(
            metadata="invalid",
        )


def test_execution_context_copies_metadata():

    metadata = {
        "source": "test",
    }

    context = ReportExecutionContext(
        metadata=metadata,
    )

    metadata["changed"] = True

    assert (
        "changed"
        not in context.metadata
    )


def test_execution_context_to_dict():

    context = ReportExecutionContext(
        correlation_id="corr-001",
        requested_by="user-001",
        source="web",
        metadata={
            "environment": "test",
        },
    )

    result = context.to_dict()

    assert (
        result["correlation_id"]
        == "corr-001"
    )

    assert (
        result["requested_by"]
        == "user-001"
    )

    assert (
        result["source"]
        == "web"
    )

    assert (
        result["metadata"]["environment"]
        == "test"
    )


def test_execution_context_is_immutable():

    context = ReportExecutionContext(
        correlation_id="corr-001",
    )

    with pytest.raises(
        AttributeError
    ):

        context.correlation_id = "changed"
