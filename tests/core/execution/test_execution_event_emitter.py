"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.10.2

Execution event emission tests.
"""

import pytest

from app.core.execution import (
    ExecutionContext,
)

from app.core.execution.events import (
    ExecutionEvent,
    ExecutionEventType,
)

from app.core.execution.event_emitter import (
    ExecutionEventEmitter,
    RecordingExecutionEventEmitter,
)


def build_context():
    """
    Build a valid execution context for emitter tests.
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


def build_event():
    """
    Build a valid execution event.
    """

    return ExecutionEvent(
        event_type=ExecutionEventType.STARTED,
        command_name="test.command",
        context=build_context(),
        outcome="success",
    )


def test_event_emitter_is_abstract():
    """
    The event emitter defines an abstract emission contract.
    """

    with pytest.raises(TypeError):
        ExecutionEventEmitter()


def test_recording_event_emitter_stores_events():
    """
    The recording emitter stores emitted events.
    """

    emitter = RecordingExecutionEventEmitter()
    event = build_event()

    emitter.emit(event)

    assert emitter.events == [event]
    assert emitter.count() == 1


def test_recording_event_emitter_preserves_emission_order():
    """
    Events are retained in the order in which they are emitted.
    """

    emitter = RecordingExecutionEventEmitter()

    first = build_event()

    second = ExecutionEvent(
        event_type=ExecutionEventType.COMPLETED,
        command_name="test.command",
        context=build_context(),
        outcome="success",
    )

    emitter.emit(first)
    emitter.emit(second)

    assert emitter.events == [
        first,
        second,
    ]


def test_recording_event_emitter_rejects_invalid_event():
    """
    The emitter requires an ExecutionEvent instance.
    """

    emitter = RecordingExecutionEventEmitter()

    with pytest.raises(
        TypeError,
        match="event",
    ):
        emitter.emit(object())


def test_recording_event_emitter_clear_removes_events():
    """
    Clearing the emitter removes all recorded events.
    """

    emitter = RecordingExecutionEventEmitter()

    emitter.emit(build_event())

    assert emitter.count() == 1

    emitter.clear()

    assert emitter.events == []
    assert emitter.count() == 0
