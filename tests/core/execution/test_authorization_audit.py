"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.8.8.1

Authorization audit contract tests.
"""

from app.core.execution import (
    AuthorizationDecision,
    BaseCommand,
    ExecutionContext,
)

from app.core.execution.authorization_audit import (
    AuthorizationAuditContract,
)


class TestAuthorizationCommand(
    BaseCommand
):
    """
    Test command for authorization audit tests.
    """

    command_name = (
        "test.authorization.audit"
    )

    permission_code = (
        "test.authorization.execute"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented
        by this test command.
        """

        return self.command_name


def build_context():
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="authorization",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "original": True,
        },
    )


def test_allowed_decision_builds_success_audit_event():
    """
    Allowed authorization produces a successful
    security audit event.
    """

    contract = AuthorizationAuditContract()

    command = TestAuthorizationCommand()

    context = build_context()

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
        metadata={
            "permission": "test.execute",
        },
    )

    event = contract.build_event(
        command,
        context,
        decision,
    )

    assert event.event_type == (
        "EXECUTION_AUTHORIZATION"
    )

    assert event.subject == "user-001"

    assert event.resource == (
        "test.authorization.audit"
    )

    assert event.action == (
        "authorization"
    )

    assert event.result == "SUCCESS"

    assert event.is_success()

    assert event.metadata[
        "authorization_allowed"
    ] is True

    assert event.metadata[
        "authorization_reason"
    ] == "Permission granted."

    assert event.metadata[
        "permission_code"
    ] == ""

    assert event.metadata[
        "original"
    ] is True

    assert event.metadata[
        "authorization_metadata"
    ][
        "permission"
    ] == "test.execute"


def test_denied_decision_builds_failed_audit_event():
    """
    Denied authorization produces a failed
    security audit event.
    """

    contract = AuthorizationAuditContract()

    command = TestAuthorizationCommand()

    context = build_context()

    decision = AuthorizationDecision.deny(
        reason="Permission denied.",
        metadata={
            "permission": "test.execute",
        },
    )

    event = contract.build_event(
        command,
        context,
        decision,
    )

    assert event.event_type == (
        "EXECUTION_AUTHORIZATION"
    )

    assert event.subject == "user-001"

    assert event.resource == (
        "test.authorization.audit"
    )

    assert event.result == "FAILED"

    assert event.is_failure()

    assert event.metadata[
        "authorization_allowed"
    ] is False

    assert event.metadata[
        "authorization_reason"
    ] == "Permission denied."


def test_context_metadata_is_preserved():
    """
    Existing execution context metadata is preserved
    in the authorization audit event.
    """

    contract = AuthorizationAuditContract()

    command = TestAuthorizationCommand()

    context = build_context()

    decision = AuthorizationDecision.allow(
        reason="Authorized."
    )

    event = contract.build_event(
        command,
        context,
        decision,
    )

    assert event.metadata[
        "original"
    ] is True

    assert event.metadata[
        "request_id"
    ] == "request-001"

    assert event.metadata[
        "correlation_id"
    ] == "correlation-001"

    assert event.metadata[
        "trace_id"
    ] == "trace-001"

    assert event.metadata[
        "environment"
    ] == "testing"
