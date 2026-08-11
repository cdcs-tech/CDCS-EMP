"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.10.1

Execution event contract tests.
"""

from datetime import datetime, timezone

import pytest

from app.core.execution import (
    ExecutionContext,
)

from app.core.execution.events import (
    ExecutionEvent,
    ExecutionEventType,
)


def build_context():
    """
    Build a valid execution context for event tests.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="execution",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
    )


def test_execution_event_requires_valid_event_type():
    """
    An execution event requires a valid event type.
    """

    with pytest.raises(
        TypeError,
        match="event_type",
    ):
        ExecutionEvent(
            event_type="execution.started",
            command_name="test.command",
            context=build_context(),
            outcome="success",
        )


def test_execution_event_requires_command_name():
    """
    An execution event requires a non-empty command name.
    """

    with pytest.raises(
        ValueError,
        match="command_name",
    ):
        ExecutionEvent(
            event_type=ExecutionEventType.STARTED,
            command_name="",
            context=build_context(),
            outcome="success",
        )


def test_execution_event_requires_execution_context():
    """
    An execution event requires an ExecutionContext.
    """

    with pytest.raises(
        TypeError,
        match="context",
    ):
        ExecutionEvent(
            event_type=ExecutionEventType.STARTED,
            command_name="test.command",
            context=object(),
            outcome="success",
        )


def test_execution_event_requires_outcome():
    """
    An execution event requires a non-empty outcome.
    """

    with pytest.raises(
        ValueError,
        match="outcome",
    ):
        ExecutionEvent(
            event_type=ExecutionEventType.COMPLETED,
            command_name="test.command",
            context=build_context(),
            outcome="",
        )


def test_execution_event_requires_valid_timestamp():
    """
    An execution event requires a datetime timestamp.
    """

    with pytest.raises(
        TypeError,
        match="timestamp",
    ):
        ExecutionEvent(
            event_type=ExecutionEventType.STARTED,
            command_name="test.command",
            context=build_context(),
            outcome="success",
            timestamp="invalid",
        )


def test_execution_event_requires_metadata_dictionary():
    """
    An execution event requires dictionary metadata.
    """

    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        ExecutionEvent(
            event_type=ExecutionEventType.STARTED,
            command_name="test.command",
            context=build_context(),
            outcome="success",
            metadata=[],
        )


def test_execution_event_defaults_timestamp_to_utc():
    """
    Execution events receive a UTC timestamp by default.
    """

    event = ExecutionEvent(
        event_type=ExecutionEventType.STARTED,
        command_name="test.command",
        context=build_context(),
        outcome="success",
    )

    assert isinstance(
        event.timestamp,
        datetime,
    )

    assert event.timestamp.tzinfo is timezone.utc


def test_execution_event_copies_metadata():
    """
    Event metadata is isolated from the source dictionary.
    """

    metadata = {
        "source": "dispatcher",
    }

    event = ExecutionEvent(
        event_type=ExecutionEventType.STARTED,
        command_name="test.command",
        context=build_context(),
        outcome="success",
        metadata=metadata,
    )

    metadata["source"] = "changed"

    assert event.metadata == {
        "source": "dispatcher",
    }


def test_execution_event_success_outcome():
    """
    A successful event identifies itself as successful.
    """

    event = ExecutionEvent(
        event_type=ExecutionEventType.COMPLETED,
        command_name="test.command",
        context=build_context(),
        outcome="success",
    )

    assert event.is_success() is True
    assert event.is_failure() is False
    assert event.is_denied() is False


def test_execution_event_failure_outcome():
    """
    A failed event identifies itself as failed.
    """

    event = ExecutionEvent(
        event_type=ExecutionEventType.FAILED,
        command_name="test.command",
        context=build_context(),
        outcome="failure",
    )

    assert event.is_success() is False
    assert event.is_failure() is True
    assert event.is_denied() is False


def test_execution_event_denied_outcome():
    """
    A denied event identifies itself as denied.
    """

    event = ExecutionEvent(
        event_type=ExecutionEventType.DENIED,
        command_name="test.command",
        context=build_context(),
        outcome="denied",
    )

    assert event.is_success() is False
    assert event.is_failure() is False
    assert event.is_denied() is True


def test_execution_event_with_metadata_returns_enriched_copy():
    """
    Event metadata can be enriched without mutating the
    original event.
    """

    event = ExecutionEvent(
        event_type=ExecutionEventType.COMPLETED,
        command_name="test.command",
        context=build_context(),
        outcome="success",
        metadata={
            "source": "dispatcher",
        },
    )

    enriched = event.with_metadata(
        duration_ms=25,
        transaction="committed",
    )

    assert event.metadata == {
        "source": "dispatcher",
    }

    assert enriched.metadata == {
        "source": "dispatcher",
        "duration_ms": 25,
        "transaction": "committed",
    }

    assert enriched.event_type is event.event_type
    assert enriched.command_name == event.command_name
    assert enriched.context is event.context
    assert enriched.outcome == event.outcome
    assert enriched.timestamp == event.timestamp
