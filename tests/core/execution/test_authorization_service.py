"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.8.6

Focused tests for role/assignment-aware execution
authorization.
"""

from __future__ import annotations

import pytest

from app.core.execution.authorization import (
    AuthorizationDecision,
    ExecutionAuthorizer,
    RoleAssignmentExecutionAuthorizer,
)

from app.core.execution.authorization_service import (
    ExecutionAuthorizationService,
)

from app.core.execution.commands.base import (
    BaseCommand,
)

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.exceptions import (
    ExecutionContractException,
)


class TestCommand(BaseCommand):
    """
    Test command used by authorization tests.
    """

    command_name = "test.role_assignment_operation"

    permission_code = (
        "test.role_assignment_operation.execute"
    )

    def execute_name(self) -> str:
        """
        Return the test operation name.
        """

        return "test.role_assignment_operation"


class FakeAuthorizationEngine:
    """
    Minimal authorization-engine double.

    Mirrors the existing AuthorizationEngine.can()
    contract.
    """

    def __init__(
        self,
        allowed: bool = True,
    ) -> None:

        self.allowed = allowed
        self.calls: list[dict] = []

    def can(
        self,
        subject,
        permission_code: str,
        policies=None,
        context=None,
    ) -> bool:
        """
        Evaluate a permission request.
        """

        self.calls.append(
            {
                "subject": subject,
                "permission_code": permission_code,
                "policies": policies,
                "context": context,
            }
        )

        return self.allowed


def build_command() -> TestCommand:
    """
    Build a valid test command.
    """

    return TestCommand()


def build_context(
    user_id: str = "user-001",
) -> ExecutionContext:
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id=user_id,
        module_name="test",
        operation="role_assignment_operation",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "source": "unit-test",
        },
    )


def test_role_assignment_authorizer_allows_authorized_user():
    """
    An authorized subject should receive an allowed decision.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    command = build_command()
    context = build_context()

    decision = authorizer.authorize(
        command,
        context,
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_allowed()
    assert not decision.is_denied()

    assert (
        decision.metadata[
            "user_id"
        ]
        == "user-001"
    )

    assert (
        decision.metadata[
            "permission_code"
        ]
        == TestCommand.permission_code
    )


def test_role_assignment_authorizer_denies_unauthorized_user():
    """
    An unauthorized subject should receive a denied decision.
    """

    engine = FakeAuthorizationEngine(
        allowed=False
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    command = build_command()
    context = build_context()

    decision = authorizer.authorize(
        command,
        context,
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_denied()
    assert not decision.is_allowed()

    assert (
        decision.metadata[
            "permission_code"
        ]
        == TestCommand.permission_code
    )


def test_authorization_engine_receives_context():
    """
    The execution context must be forwarded to the
    existing AuthorizationEngine.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    command = build_command()
    context = build_context()

    authorizer.authorize(
        command,
        context,
    )

    assert len(
        engine.calls
    ) == 1

    call = engine.calls[0]

    assert (
        call["subject"]
        == context.user_id
    )

    assert (
        call["permission_code"]
        == TestCommand.permission_code
    )

    assert (
        call["context"]
        is context
    )


def test_authorization_service_delegates_to_authorizer():
    """
    ExecutionAuthorizationService should delegate
    authorization to the configured authorizer.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    service = ExecutionAuthorizationService(
        authorizer
    )

    command = build_command()
    context = build_context()

    decision = service.authorize(
        command,
        context,
    )

    assert decision.is_allowed()

    assert len(
        engine.calls
    ) == 1


def test_authorization_service_is_allowed():
    """
    is_allowed() should return the authorization decision
    as a boolean.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    service = ExecutionAuthorizationService(
        authorizer
    )

    assert service.is_allowed(
        build_command(),
        build_context(),
    )


def test_authorization_service_denies_when_permission_fails():
    """
    is_allowed() should return False when permission
    evaluation fails.
    """

    engine = FakeAuthorizationEngine(
        allowed=False
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    service = ExecutionAuthorizationService(
        authorizer
    )

    assert not service.is_allowed(
        build_command(),
        build_context(),
    )


def test_missing_user_identity_is_denied():
    """
    Role/assignment-aware authorization requires
    a user identity.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    context = build_context(
        user_id=""
    )

    decision = authorizer.authorize(
        build_command(),
        context,
    )

    assert decision.is_denied()

    assert (
        len(engine.calls)
        == 0
    )


def test_missing_permission_is_denied():
    """
    A command without a required permission must
    not be authorized.
    """

    class NoPermissionCommand(
        BaseCommand
    ):
        command_name = (
            "test.no_permission"
        )

        def execute_name(self) -> str:
            return "test.no_permission"

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    decision = authorizer.authorize(
        NoPermissionCommand(),
        build_context(),
    )

    assert decision.is_denied()

    assert (
        len(engine.calls)
        == 0
    )


def test_invalid_authorization_engine_is_rejected():
    """
    The role/assignment authorizer must reject an
    object that does not provide AuthorizationEngine.can().
    """

    with pytest.raises(
        ExecutionContractException
    ):
        RoleAssignmentExecutionAuthorizer(
            object()
        )


def test_require_authorization_allows_valid_request():
    """
    require_authorization() should return the decision
    when authorization succeeds.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    service = ExecutionAuthorizationService(
        authorizer
    )

    decision = service.require_authorization(
        build_command(),
        build_context(),
    )

    assert decision.is_allowed()


def test_require_authorization_rejects_denied_request():
    """
    require_authorization() should raise when authorization
    is denied.
    """

    engine = FakeAuthorizationEngine(
        allowed=False
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    service = ExecutionAuthorizationService(
        authorizer
    )

    with pytest.raises(
        ExecutionContractException
    ):
        service.require_authorization(
            build_command(),
            build_context(),
        )


def test_authorization_metadata_is_available():
    """
    Authorization metadata should be exposed by the
    service without modifying the original decision.
    """

    engine = FakeAuthorizationEngine(
        allowed=True
    )

    authorizer = (
        RoleAssignmentExecutionAuthorizer(
            engine
        )
    )

    service = ExecutionAuthorizationService(
        authorizer
    )

    metadata = service.metadata(
        build_command(),
        build_context(),
    )

    assert (
        metadata["user_id"]
        == "user-001"
    )

    assert (
        metadata["permission_code"]
        == TestCommand.permission_code
    )

    assert (
        metadata["authorization_source"]
        == "AuthorizationEngine"
    )
