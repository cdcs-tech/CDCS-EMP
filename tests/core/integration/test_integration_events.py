"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration event tests.
"""

from app.core.events.registry import (
    EventRegistry,
)

from app.core.integration import (
    IntegrationFailureEvent,
    IntegrationRequest,
    IntegrationRequestEvent,
    IntegrationResultEvent,
)

from app.core.integration.event_hook import (
    IntegrationEventHook,
)

from app.core.integration.models import (
    IntegrationResponse,
    IntegrationResult,
)


class RecordingPublisher:
    """
    Test publisher that records published events.
    """

    def __init__(self):
        self.events = []

    def publish(
        self,
        event,
    ):
        self.events.append(
            event
        )

        return event


def create_request():

    return IntegrationRequest(
        provider="test_provider",
        operation="create",
    )


def create_result(
    request,
    success=True,
):

    response = IntegrationResponse(
        success=success,
        status_code=(
            200
            if success
            else 500
        ),
        request_id=request.request_id,
    )

    return IntegrationResult(
        request=request,
        response=response,
        duration_ms=12.5,
        provider=request.provider,
        operation=request.operation,
    )


def test_request_event():

    request = create_request()

    event = IntegrationRequestEvent(
        request=request,
        subject="system",
    )

    assert (
        event.event_name
        == "integration.request"
    )

    metadata = event.metadata()

    assert (
        metadata["request_id"]
        == request.request_id
    )

    assert (
        metadata["provider"]
        == "test_provider"
    )

    assert (
        metadata["operation"]
        == "create"
    )


def test_result_event():

    request = create_request()

    result = create_result(
        request
    )

    event = IntegrationResultEvent(
        result=result,
        subject="system",
    )

    assert (
        event.event_name
        == "integration.result"
    )

    metadata = event.metadata()

    assert (
        metadata["success"]
        is True
    )

    assert (
        metadata["duration_ms"]
        == 12.5
    )


def test_failure_event():

    request = create_request()

    event = IntegrationFailureEvent(
        request=request,
        message="Provider unavailable.",
        subject="system",
        metadata={
            "exception": "TimeoutError"
        },
    )

    assert (
        event.event_name
        == "integration.failure"
    )

    metadata = event.metadata()

    assert (
        metadata["message"]
        == "Provider unavailable."
    )

    assert (
        metadata["details"]["exception"]
        == "TimeoutError"
    )


def test_event_hook_publishes_request():

    publisher = RecordingPublisher()

    hook = IntegrationEventHook(
        publisher=publisher
    )

    request = create_request()

    result = hook.publish_request(
        request
    )

    assert len(
        publisher.events
    ) == 1

    assert isinstance(
        publisher.events[0],
        IntegrationRequestEvent,
    )

    assert (
        result
        is publisher.events[0]
    )


def test_event_hook_publishes_result():

    publisher = RecordingPublisher()

    hook = IntegrationEventHook(
        publisher=publisher
    )

    request = create_request()

    integration_result = create_result(
        request
    )

    hook.publish_result(
        integration_result
    )

    assert len(
        publisher.events
    ) == 1

    assert isinstance(
        publisher.events[0],
        IntegrationResultEvent,
    )


def test_event_hook_publishes_failure():

    publisher = RecordingPublisher()

    hook = IntegrationEventHook(
        publisher=publisher
    )

    request = create_request()

    hook.publish_failure(
        request,
        message="Integration failed.",
    )

    assert len(
        publisher.events
    ) == 1

    event = (
        publisher.events[0]
    )

    assert isinstance(
        event,
        IntegrationFailureEvent,
    )

    assert (
        event.message
        == "Integration failed."
    )


def test_events_can_be_registered():

    registry = EventRegistry()

    registry.register(
        IntegrationRequestEvent
    )

    registry.register(
        IntegrationResultEvent
    )

    registry.register(
        IntegrationFailureEvent
    )

    assert (
        registry.get_event(
            "integration.request"
        )
        is IntegrationRequestEvent
    )

    assert (
        registry.get_event(
            "integration.result"
        )
        is IntegrationResultEvent
    )

    assert (
        registry.get_event(
            "integration.failure"
        )
        is IntegrationFailureEvent
    )

