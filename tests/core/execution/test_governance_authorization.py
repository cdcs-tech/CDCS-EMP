"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.11.5

Governance and authorization integration tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    CommandDispatcher,
    ExecutionAuthorizer,
    ExecutionContext,
    ExecutionContractException,
    ExecutionGovernance,
    ExecutionResult,
    GovernanceAwareAuthorizationEnforcement,
)

from app.core.execution.authorization import (
    AuthorizationDecision,
)

from app.core.execution.authorization_service import (
    ExecutionAuthorizationService,
)

from app.core.execution.event_emitter import (
    RecordingExecutionEventEmitter,
)

from app.core.execution.events import (
    ExecutionEventType,
)

from app.core.execution.transaction import (
    ExecutionTransactionBoundary,
)


class GovernanceAuthorizationCommand(
    BaseCommand
):
    """
    Test command used for governance and
    authorization integration tests.
    """

    command_name = (
        "test.governance.authorization"
    )

    permission_code = (
        "test.governance.authorization"
    )

    def execute_name(self) -> str:
        """
        Return the operation represented by
        this command.
        """

        return self.command_name


class TrackingHandler(
    BaseCommandHandler
):
    """
    Handler that records whether execution
    occurred.
    """

    command_type = (
        GovernanceAuthorizationCommand
    )

    def __init__(self):
        self.called = False

    def handle(
        self,
        command,
        context,
    ):
        self.called = True

        return ExecutionResult.success_result(
            data={
                "executed": True,
            },
            message="Execution completed.",
        )


class AllowingAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that explicitly allows execution.
    """

    def authorize(
        self,
        command,
        context,
    ):
        return AuthorizationDecision.allow(
            reason="Permission granted.",
            metadata={
                "authorization_source": (
                    "test"
                ),
            },
        )


class DenyingAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that explicitly denies execution.
    """

    def authorize(
        self,
        command,
        context,
    ):
        return AuthorizationDecision.deny(
            reason="Permission denied.",
            metadata={
                "authorization_source": (
                    "test"
                ),
            },
        )


class FailingAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that raises an unexpected
    authorization exception.
    """

    def authorize(
        self,
        command,
        context,
    ):
        raise RuntimeError(
            "authorization evaluation failed"
        )


class TrackingAuthorizer(
    ExecutionAuthorizer
):
    """
    Authorizer that records authorization
    service calls.
    """

    def __init__(
        self,
        decision,
    ):
        self.decision = decision
        self.calls = []

    def authorize(
        self,
        command,
        context,
    ):
        self.calls.append(
            (
                command,
                context,
            )
        )

        return self.decision


class RecordingTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Transaction boundary that records
    lifecycle operations.
    """

    def __init__(self):
        self.events = []

    def begin(self) -> None:
        self.events.append("begin")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")


class TrackingGovernance(
    ExecutionGovernance
):
    """
    Governance implementation that records
    authorization governance calls.
    """

    def __init__(self):
        super().__init__()

        self.audit_calls = []
        self.result_calls = []

    def audit_event(
        self,
        command,
        context,
        decision,
    ):
        self.audit_calls.append(
            (
                command,
                context,
                decision,
            )
        )

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
        self.result_calls.append(
            (
                decision,
                context,
            )
        )

        return super().governed_result(
            decision,
            context=context,
            data=data,
            message=message,
            error_code=error_code,
            result_metadata=result_metadata,
        )


@pytest.fixture(autouse=True)
def cleanup_command_registry():
    """
    Ensure the shared command registry is isolated
    between tests.
    """

    from app.core.execution import (
        command_registry,
    )

    command_name = (
        GovernanceAuthorizationCommand.command_name
    )

    if command_registry.exists(
        command_name
    ):
        command_registry.unregister(
            command_name
        )

    yield

    if command_registry.exists(
        command_name
    ):
        command_registry.unregister(
            command_name
        )


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
        metadata={},
    )


def build_dispatcher(
    handler,
    *,
    authorizer=None,
    authorization_enforcement=None,
    emitter=None,
    transaction_boundary=None,
):
    """
    Build a dispatcher configured for
    governance and authorization tests.
    """

    dispatcher = CommandDispatcher(
        authorizer=authorizer,
        authorization_enforcement=(
            authorization_enforcement
        ),
        event_emitter=emitter,
        transaction_boundary=(
            transaction_boundary
        ),
    )

    dispatcher.registry.register(
        GovernanceAuthorizationCommand
    )

    dispatcher.register_handler(
        handler
    )

    return dispatcher


def test_authorization_allow_permits_execution():
    """
    An allowed authorization decision permits
    normal command execution.
    """

    handler = TrackingHandler()

    dispatcher = build_dispatcher(
        handler,
        authorizer=AllowingAuthorizer(),
    )

    result = dispatcher.dispatch(
        GovernanceAuthorizationCommand(),
        build_context(),
    )

    assert result.is_success()
    assert handler.called is True


def test_authorization_denial_reaches_denied_lifecycle():
    """
    Authorization denial produces STARTED followed
    by DENIED execution lifecycle events.
    """

    emitter = RecordingExecutionEventEmitter()

    handler = TrackingHandler()

    dispatcher = build_dispatcher(
        handler,
        authorizer=DenyingAuthorizer(),
        emitter=emitter,
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceAuthorizationCommand(),
            build_context(),
        )

    assert handler.called is False

    assert [
        event.event_type
        for event in emitter.events
    ] == [
        ExecutionEventType.STARTED,
        ExecutionEventType.DENIED,
    ]


def test_authorization_denial_does_not_begin_transaction():
    """
    Authorization denial occurs before the
    transaction boundary begins.
    """

    transaction = RecordingTransactionBoundary()

    handler = TrackingHandler()

    dispatcher = build_dispatcher(
        handler,
        authorizer=DenyingAuthorizer(),
        transaction_boundary=transaction,
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceAuthorizationCommand(),
            build_context(),
        )

    assert handler.called is False
    assert transaction.events == []


def test_authorization_denial_preserves_decision_metadata():
    """
    Authorization decisions preserve their own
    metadata independently of dispatcher execution.
    """

    decision = DenyingAuthorizer().authorize(
        GovernanceAuthorizationCommand(),
        build_context(),
    )

    assert decision.is_denied()

    assert (
        decision.metadata[
            "authorization_source"
        ]
        == "test"
    )


def test_governance_aware_enforcement_uses_governance():
    """
    Governance-aware authorization enforcement
    delegates audit and result construction to
    ExecutionGovernance.
    """

    authorizer = AllowingAuthorizer()

    service = ExecutionAuthorizationService(
        authorizer=authorizer,
    )

    governance = TrackingGovernance()

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
            governance=governance,
        )
    )

    command = GovernanceAuthorizationCommand()
    context = build_context()

    decision, event, result = (
        enforcement.enforce(
            command,
            context,
        )
    )

    assert decision.is_allowed()
    assert event is not None
    assert result.is_success()

    assert len(
        governance.audit_calls
    ) == 1

    assert len(
        governance.result_calls
    ) == 1

    assert (
        governance.audit_calls[0][0]
        is command
    )

    assert (
        governance.audit_calls[0][1]
        is context
    )

    assert (
        governance.audit_calls[0][2]
        is decision
    )

    assert (
        governance.result_calls[0][0]
        is decision
    )

    assert (
        governance.result_calls[0][1]
        is context
    )


def test_governance_aware_denial_produces_governed_failure_result():
    """
    A denied authorization decision is converted
    into a governed failure result.
    """

    service = ExecutionAuthorizationService(
        authorizer=DenyingAuthorizer(),
    )

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
        )
    )

    decision, event, result = (
        enforcement.enforce(
            GovernanceAuthorizationCommand(),
            build_context(),
        )
    )

    assert decision.is_denied()
    assert event is not None

    assert result.is_failure()

    assert (
        result.error_code
        == "AUTHORIZATION_DENIED"
    )


def test_governance_aware_allow_produces_governed_success_result():
    """
    An allowed authorization decision is converted
    into a governed success result.
    """

    service = ExecutionAuthorizationService(
        authorizer=AllowingAuthorizer(),
    )

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
        )
    )

    decision, event, result = (
        enforcement.enforce(
            GovernanceAuthorizationCommand(),
            build_context(),
        )
    )

    assert decision.is_allowed()
    assert event is not None
    assert result.is_success()


def test_governance_aware_authorization_uses_service():
    """
    Governance-aware enforcement delegates
    authorization evaluation to the configured
    ExecutionAuthorizationService.
    """

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
    )

    authorizer = TrackingAuthorizer(
        decision
    )

    service = ExecutionAuthorizationService(
        authorizer=authorizer,
    )

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
        )
    )

    command = GovernanceAuthorizationCommand()
    context = build_context()

    result = enforcement.authorize(
        command,
        context,
    )

    assert result is decision

    assert len(
        authorizer.calls
    ) == 1

    assert (
        authorizer.calls[0][0]
        is command
    )

    assert (
        authorizer.calls[0][1]
        is context
    )


def test_authorization_failure_becomes_contract_failure():
    """
    An unexpected authorization exception is
    converted into an execution contract failure.
    """

    handler = TrackingHandler()

    dispatcher = build_dispatcher(
        handler,
        authorizer=FailingAuthorizer(),
    )

    with pytest.raises(
        ExecutionContractException,
        match="Authorization evaluation failed.",
    ):
        dispatcher.dispatch(
            GovernanceAuthorizationCommand(),
            build_context(),
        )

    assert handler.called is False


def test_governance_aware_enforcement_rejects_invalid_decision():
    """
    Governance-aware result generation rejects
    objects that are not AuthorizationDecision
    instances.
    """

    service = ExecutionAuthorizationService(
        authorizer=AllowingAuthorizer(),
    )

    enforcement = (
        GovernanceAwareAuthorizationEnforcement(
            authorization_service=service,
        )
    )

    with pytest.raises(
        TypeError,
        match=(
            "decision must be an "
            "AuthorizationDecision"
        ),
    ):
        enforcement.result(
            object()
        )


def test_authorization_denial_emits_started_then_denied():
    """
    Authorization denial emits STARTED followed
    by DENIED and prevents handler execution.
    """

    emitter = RecordingExecutionEventEmitter()

    handler = TrackingHandler()

    dispatcher = build_dispatcher(
        handler,
        authorizer=DenyingAuthorizer(),
        emitter=emitter,
    )

    with pytest.raises(
        ExecutionContractException,
        match="Permission denied.",
    ):
        dispatcher.dispatch(
            GovernanceAuthorizationCommand(),
            build_context(),
        )

    assert handler.called is False

    assert len(
        emitter.events
    ) == 2

    assert (
        emitter.events[0].event_type
        is ExecutionEventType.STARTED
    )

    assert (
        emitter.events[1].event_type
        is ExecutionEventType.DENIED
    )
