"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.8.10.1

Execution governance integration contract tests.
"""

from app.core.execution import (
    AuthorizationDecision,
    BaseCommand,
    ExecutionContext,
    ExecutionGovernance,
)


class TestGovernanceCommand(BaseCommand):
    """
    Test command for execution governance tests.
    """

    command_name = (
        "test.governance.execute"
    )

    permission_code = (
        "test.governance.execute"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented
        by this command.
        """

        return self.command_name


def build_context() -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="governance",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "original": True,
        },
    )


def test_allowed_decision_produces_success_result():
    """
    An allowed authorization decision produces
    a successful governed execution result.
    """

    governance = ExecutionGovernance()

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
        metadata={
            "permission_code": (
                "test.governance.execute"
            ),
        },
    )

    context = build_context()

    result = governance.governed_result(
        decision,
        context=context,
        data={
            "executed": True,
        },
    )

    assert result.success is True

    assert result.metadata[
        "authorization_allowed"
    ] is True

    assert result.metadata[
        "authorization_reason"
    ] == "Permission granted."

    assert result.metadata[
        "user_id"
    ] == "user-001"

    assert result.metadata[
        "original"
    ] is True


def test_denied_decision_produces_failure_result():
    """
    A denied authorization decision produces
    a governed authorization failure result.
    """

    governance = ExecutionGovernance()

    decision = AuthorizationDecision.deny(
        reason="Permission denied.",
        metadata={
            "permission_code": (
                "test.governance.execute"
            ),
        },
    )

    context = build_context()

    result = governance.governed_result(
        decision,
        context=context,
    )

    assert result.success is False

    assert result.error_code == (
        "AUTHORIZATION_DENIED"
    )

    assert result.metadata[
        "authorization_allowed"
    ] is False

    assert result.metadata[
        "authorization_reason"
    ] == "Permission denied."


def test_authorization_audit_event_is_built():
    """
    Governance delegates audit construction to
    the existing authorization audit contract.
    """

    governance = ExecutionGovernance()

    command = TestGovernanceCommand()

    context = build_context()

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
    )

    event = governance.audit_event(
        command,
        context,
        decision,
    )

    assert event.event_type == (
        "EXECUTION_AUTHORIZATION"
    )

    assert event.subject == "user-001"

    assert event.resource == (
        "test.governance.execute"
    )

    assert event.action == (
        "governance"
    )

    assert event.result == "SUCCESS"


def test_governance_metadata_preserves_context():
    """
    Governance metadata preserves existing
    execution context information.
    """

    governance = ExecutionGovernance()

    decision = AuthorizationDecision.allow(
        reason="Authorized.",
    )

    context = build_context()

    metadata = governance.result_metadata(
        decision,
        context,
    )

    assert metadata[
        "authorization_allowed"
    ] is True

    assert metadata[
        "authorization_reason"
    ] == "Authorized."

    assert metadata[
        "user_id"
    ] == "user-001"

    assert metadata[
        "module_name"
    ] == "test"

    assert metadata[
        "operation"
    ] == "governance"

    assert metadata[
        "request_id"
    ] == "request-001"

    assert metadata[
        "correlation_id"
    ] == "correlation-001"

    assert metadata[
        "trace_id"
    ] == "trace-001"
