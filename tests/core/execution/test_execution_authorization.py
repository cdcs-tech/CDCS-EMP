"""
Tests for the execution authorization contract.
"""

import pytest

from app.core.execution.authorization import (
    AllowAllExecutionAuthorizer,
    AuthorizationDecision,
    ExecutionAuthorizer,
    validate_authorization_contract,
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
    Test command implementation.
    """

    command_name = "test.authorization"

    def execute_name(self) -> str:
        return "test.authorization"


def valid_context() -> ExecutionContext:
    """
    Create a valid execution context.
    """

    return ExecutionContext(
        user_id="test-user",
        module_name="test",
        operation="authorization",
    )


def test_authorization_decision_allow():
    """
    Allowed decisions report correctly.
    """

    decision = AuthorizationDecision.allow(
        reason="Allowed for testing."
    )

    assert decision.allowed is True
    assert decision.is_allowed() is True
    assert decision.is_denied() is False
    assert decision.reason == "Allowed for testing."


def test_authorization_decision_deny():
    """
    Denied decisions report correctly.
    """

    decision = AuthorizationDecision.deny(
        reason="Denied for testing."
    )

    assert decision.allowed is False
    assert decision.is_allowed() is False
    assert decision.is_denied() is True
    assert decision.reason == "Denied for testing."


def test_default_authorizer_allows_valid_execution():
    """
    The compatibility authorizer allows valid execution.
    """

    command = TestCommand()
    context = valid_context()

    authorizer = AllowAllExecutionAuthorizer()

    decision = authorizer.authorize(
        command,
        context,
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_allowed() is True


def test_authorizer_implements_contract():
    """
    The default authorizer implements the base contract.
    """

    authorizer = AllowAllExecutionAuthorizer()

    assert isinstance(
        authorizer,
        ExecutionAuthorizer,
    )


def test_validate_authorization_contract_accepts_valid_objects():
    """
    Valid authorization objects pass contract validation.
    """

    command = TestCommand()
    context = valid_context()
    authorizer = AllowAllExecutionAuthorizer()

    validate_authorization_contract(
        command,
        context,
        authorizer,
    )


def test_validate_authorization_contract_rejects_invalid_command():
    """
    Invalid commands are rejected.
    """

    context = valid_context()
    authorizer = AllowAllExecutionAuthorizer()

    with pytest.raises(
        ExecutionContractException
    ):
        validate_authorization_contract(
            object(),
            context,
            authorizer,
        )


def test_validate_authorization_contract_rejects_invalid_context():
    """
    Invalid contexts are rejected.
    """

    command = TestCommand()
    authorizer = AllowAllExecutionAuthorizer()

    with pytest.raises(
        ExecutionContractException
    ):
        validate_authorization_contract(
            command,
            object(),
            authorizer,
        )


def test_validate_authorization_contract_rejects_invalid_authorizer():
    """
    Invalid authorizers are rejected.
    """

    command = TestCommand()
    context = valid_context()

    with pytest.raises(
        ExecutionContractException
    ):
        validate_authorization_contract(
            command,
            context,
            object(),
        )


def test_default_authorizer_rejects_invalid_command():
    """
    The default authorizer rejects invalid commands.
    """

    authorizer = AllowAllExecutionAuthorizer()
    context = valid_context()

    with pytest.raises(
        ExecutionContractException
    ):
        authorizer.authorize(
            object(),
            context,
        )


def test_default_authorizer_rejects_invalid_context():
    """
    The default authorizer rejects invalid contexts.
    """

    authorizer = AllowAllExecutionAuthorizer()
    command = TestCommand()

    with pytest.raises(
        ExecutionContractException
    ):
        authorizer.authorize(
            command,
            object(),
        )
