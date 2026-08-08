"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration lifecycle tests.
"""

import pytest

from app.core.integration import (
    IntegrationAuditHook,
    IntegrationEventHook,
    IntegrationLifecycle,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
)

from app.core.integration.providers import (
    BaseIntegrationProvider,
    IntegrationProviderRegistry,
)

from app.core.integration.service import (
    IntegrationService,
)

from app.core.security.audit_registry import (
    AuditRegistry,
)


class RecordingPublisher:
    """
    Test publisher that records events.
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


class SuccessfulProvider(
    BaseIntegrationProvider
):
    """
    Provider used for successful
    lifecycle tests.
    """

    @property
    def provider_name(self):
        return "successful_provider"

    def execute(
        self,
        request,
    ):
        return IntegrationResponse(
            success=True,
            status_code=200,
            data={
                "status": "ok"
            },
        )


class FailingProvider(
    BaseIntegrationProvider
):
    """
    Provider used for lifecycle failure tests.
    """

    @property
    def provider_name(self):
        return "failing_provider"

    def execute(
        self,
        request,
    ):
        raise RuntimeError(
            "Provider execution failed."
        )


def create_lifecycle():

    registry = (
        IntegrationProviderRegistry()
    )

    registry.register(
        SuccessfulProvider()
    )

    registry.register(
        FailingProvider()
    )

    service = IntegrationService(
        provider_registry=registry
    )

    publisher = RecordingPublisher()

    event_hook = IntegrationEventHook(
        publisher=publisher
    )

    audit_registry = AuditRegistry()

    audit_hook = IntegrationAuditHook(
        registry=audit_registry
    )

    lifecycle = IntegrationLifecycle(
        service=service,
        event_hook=event_hook,
        audit_hook=audit_hook,
    )

    return (
        lifecycle,
        publisher,
        audit_registry,
    )


def test_successful_lifecycle():

    (
        lifecycle,
        publisher,
        audit_registry,
    ) = create_lifecycle()

    request = IntegrationRequest(
        provider="successful_provider",
        operation="create",
    )

    result = lifecycle.execute(
        request,
        subject="test_user",
    )

    assert isinstance(
        result,
        IntegrationResult,
    )

    assert result.success is True

    # Request event + result event
    assert len(
        publisher.events
    ) == 2

    assert (
        publisher.events[0].event_name
        == "integration.request"
    )

    assert (
        publisher.events[1].event_name
        == "integration.result"
    )

    # Request audit + result audit
    assert (
        audit_registry.count()
        == 2
    )

    assert (
        audit_registry.all()[0].event_type
        == "INTEGRATION_REQUEST"
    )

    assert (
        audit_registry.all()[1].event_type
        == "INTEGRATION_RESULT"
    )


def test_failed_lifecycle():

    (
        lifecycle,
        publisher,
        audit_registry,
    ) = create_lifecycle()

    request = IntegrationRequest(
        provider="failing_provider",
        operation="create",
    )

    with pytest.raises(
        Exception
    ):

        lifecycle.execute(
            request,
            subject="system",
        )

    # Request event + failure event
    assert len(
        publisher.events
    ) == 2

    assert (
        publisher.events[0].event_name
        == "integration.request"
    )

    assert (
        publisher.events[1].event_name
        == "integration.failure"
    )

    # Request audit + failure audit
    assert (
        audit_registry.count()
        == 2
    )

    assert (
        audit_registry.all()[0].event_type
        == "INTEGRATION_REQUEST"
    )

    assert (
        audit_registry.all()[1].event_type
        == "INTEGRATION_FAILURE"
    )

    assert (
        audit_registry.all()[1].result
        == "FAILED"
    )


def test_execute_many():

    (
        lifecycle,
        publisher,
        audit_registry,
    ) = create_lifecycle()

    requests = [
        IntegrationRequest(
            provider="successful_provider",
            operation="create",
        ),
        IntegrationRequest(
            provider="successful_provider",
            operation="update",
        ),
    ]

    results = lifecycle.execute_many(
        requests,
        subject="batch_process",
    )

    assert len(
        results
    ) == 2

    assert all(
        result.success
        for result in results
    )

    # Each request produces:
    # request event + result event
    assert len(
        publisher.events
    ) == 4

    # Each request produces:
    # request audit + result audit
    assert (
        audit_registry.count()
        == 4
    )


def test_subject_propagation():

    (
        lifecycle,
        publisher,
        audit_registry,
    ) = create_lifecycle()

    request = IntegrationRequest(
        provider="successful_provider",
        operation="create",
    )

    lifecycle.execute(
        request,
        subject="admin_user",
    )

    assert (
        publisher.events[0].subject
        == "admin_user"
    )

    assert (
        publisher.events[1].subject
        == "admin_user"
    )

    assert (
        audit_registry.all()[0].subject
        == "admin_user"
    )

    assert (
        audit_registry.all()[1].subject
        == "admin_user"
    )


def test_lifecycle_representation():

    (
        lifecycle,
        _publisher,
        _audit_registry,
    ) = create_lifecycle()

    representation = repr(
        lifecycle
    )

    assert (
        "IntegrationLifecycle"
        in representation
    )

    assert (
        "service="
        in representation
    )

    assert (
        "event_hook="
        in representation
    )

    assert (
        "audit_hook="
        in representation
    )

