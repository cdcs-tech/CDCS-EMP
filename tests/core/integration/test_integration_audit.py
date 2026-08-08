"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Integration Framework Tests

Integration audit hook tests.
"""

from app.core.integration import (
    IntegrationAuditHook,
    IntegrationRequest,
)

from app.core.integration.models import (
    IntegrationResponse,
    IntegrationResult,
)

from app.core.security.audit import (
    SecurityAuditEvent,
)

from app.core.security.audit_registry import (
    AuditRegistry,
)


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
        request_id=(
            request.request_id
        ),
    )

    return IntegrationResult(
        request=request,
        response=response,
        duration_ms=25.5,
        provider=request.provider,
        operation=request.operation,
    )


def test_record_request():

    registry = AuditRegistry()

    hook = IntegrationAuditHook(
        registry=registry
    )

    request = create_request()

    event = hook.record_request(
        request,
        subject="test_user",
    )

    assert isinstance(
        event,
        SecurityAuditEvent,
    )

    assert (
        event.event_type
        == "INTEGRATION_REQUEST"
    )

    assert (
        event.subject
        == "test_user"
    )

    assert (
        event.resource
        == "test_provider"
    )

    assert (
        event.action
        == "create"
    )

    assert (
        event.result
        == "SUCCESS"
    )

    assert (
        event.metadata["request_id"]
        == request.request_id
    )

    assert registry.count() == 1


def test_record_successful_result():

    registry = AuditRegistry()

    hook = IntegrationAuditHook(
        registry=registry
    )

    request = create_request()

    result = create_result(
        request,
        success=True,
    )

    event = hook.record_result(
        result,
        subject="system",
    )

    assert (
        event.event_type
        == "INTEGRATION_RESULT"
    )

    assert (
        event.result
        == "SUCCESS"
    )

    assert (
        event.metadata["duration_ms"]
        == 25.5
    )

    assert registry.count() == 1


def test_record_failed_result():

    registry = AuditRegistry()

    hook = IntegrationAuditHook(
        registry=registry
    )

    request = create_request()

    result = create_result(
        request,
        success=False,
    )

    event = hook.record_result(
        result
    )

    assert (
        event.event_type
        == "INTEGRATION_RESULT"
    )

    assert (
        event.result
        == "FAILED"
    )

    assert event.is_failure()

    assert registry.count() == 1


def test_record_failure():

    registry = AuditRegistry()

    hook = IntegrationAuditHook(
        registry=registry
    )

    request = create_request()

    event = hook.record_failure(
        request,
        message="Provider unavailable.",
        subject="system",
        metadata={
            "exception": "TimeoutError"
        },
    )

    assert (
        event.event_type
        == "INTEGRATION_FAILURE"
    )

    assert (
        event.result
        == "FAILED"
    )

    assert (
        event.message
        == "Provider unavailable."
    )

    assert (
        event.metadata["exception"]
        == "TimeoutError"
    )

    assert registry.count() == 1


def test_audit_events_can_be_filtered():

    registry = AuditRegistry()

    hook = IntegrationAuditHook(
        registry=registry
    )

    request = create_request()

    hook.record_request(
        request
    )

    hook.record_failure(
        request,
        message="Failure",
    )

    failures = registry.filter(
        event_type="INTEGRATION_FAILURE"
    )

    assert len(
        failures
    ) == 1

    assert (
        failures[0].result
        == "FAILED"
    )


def test_audit_hook_repr():

    registry = AuditRegistry()

    hook = IntegrationAuditHook(
        registry=registry
    )

    representation = repr(
        hook
    )

    assert (
        "IntegrationAuditHook"
        in representation
    )

