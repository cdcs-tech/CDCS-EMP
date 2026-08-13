"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.8.10.2

Governance-aware authorization enforcement tests.
"""

from app.core.execution import (
    AllowAllExecutionAuthorizer,
    AuthorizationDecision,
    ExecutionAuthorizationService,
    ExecutionContext,
    ExecutionGovernance,
    GovernanceAwareAuthorizationEnforcement,
)


from app.core.execution.commands.base import (
    BaseCommand,
)


class TestEnforcementCommand(BaseCommand):
    """
    Test command for governance-aware enforcement.
    """

    command_name = (
        "test.authorization.enforcement"
    )

    permission_code = (
        "test.authorization.execute"
    )

    def execute_name(self) -> str:
        return self.command_name


def build_context() -> ExecutionContext:
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


def build_enforcement():
    service = ExecutionAuthorizationService(
        AllowAllExecutionAuthorizer()
    )

    return GovernanceAwareAuthorizationEnforcement(
        service
    )


def test_authorize_delegates_to_authorization_service():
    enforcement = build_enforcement()

    command = TestEnforcementCommand()
    context = build_context()

    decision = enforcement.authorize(
        command,
        context,
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_allowed()


def test_allowed_enforcement_builds_audit_and_success_result():
    enforcement = build_enforcement()

    command = TestEnforcementCommand()
    context = build_context()

    decision, event, result = enforcement.enforce(
        command,
        context,
        data={"executed": True},
    )

    assert decision.is_allowed()

    assert event.event_type == (
        "EXECUTION_AUTHORIZATION"
    )

    assert event.subject == "user-001"

    assert event.resource == (
        "test.authorization.enforcement"
    )

    assert event.result == "SUCCESS"

    assert result.success is True

    assert result.metadata[
        "authorization_allowed"
    ] is True


def test_denied_decision_builds_failed_result():
    class DenyingAuthorizer(
        AllowAllExecutionAuthorizer
    ):
        def authorize(
            self,
            command,
            context,
        ):
            return AuthorizationDecision.deny(
                reason="Permission denied."
            )

    service = ExecutionAuthorizationService(
        DenyingAuthorizer()
    )

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            service
        )
    )

    command = TestEnforcementCommand()
    context = build_context()

    decision, event, result = enforcement.enforce(
        command,
        context,
    )

    assert decision.is_denied()

    assert event.result == "FAILED"

    assert result.success is False

    assert result.error_code == (
        "AUTHORIZATION_DENIED"
    )

    assert result.metadata[
        "authorization_allowed"
    ] is False


def test_context_metadata_reaches_governed_result():
    enforcement = build_enforcement()

    command = TestEnforcementCommand()
    context = build_context()

    decision = enforcement.authorize(
        command,
        context,
    )

    result = enforcement.result(
        decision,
        context=context,
    )

    assert result.success is True

    assert result.metadata[
        "user_id"
    ] == "user-001"

    assert result.metadata[
        "request_id"
    ] == "request-001"

    assert result.metadata[
        "correlation_id"
    ] == "correlation-001"

    assert result.metadata[
        "trace_id"
    ] == "trace-001"

def test_enforcement_uses_supplied_execution_governance():
    class TrackingGovernance(ExecutionGovernance):
        def __init__(self):
            super().__init__()
            self.audit_called = False
            self.result_called = False

        def audit_event(
            self,
            command,
            context,
            decision,
        ):
            self.audit_called = True

            return super().audit_event(
                command,
                context,
                decision,
            )

        def governed_result(
            self,
            decision,
            *,
            context=None,
            data=None,
            message="",
            error_code="AUTHORIZATION_DENIED",
            result_metadata=None,
        ):
            self.result_called = True

            return super().governed_result(
                decision,
                context=context,
                data=data,
                message=message,
                error_code=error_code,
                result_metadata=result_metadata,
            )

    governance = TrackingGovernance()

    service = ExecutionAuthorizationService(
        AllowAllExecutionAuthorizer()
    )

    enforcement = GovernanceAwareAuthorizationEnforcement(
        service,
        governance=governance,
    )

    command = TestEnforcementCommand()
    context = build_context()

    decision, event, result = enforcement.enforce(
        command,
        context,
    )

    assert decision.is_allowed()

    assert event.event_type == (
        "EXECUTION_AUTHORIZATION"
    )

    assert result.success is True

    assert governance.audit_called is True
    assert governance.result_called is True
