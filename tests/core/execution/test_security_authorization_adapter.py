"""
Tests for the security authorization adapter.
"""

import pytest

from app.core.execution.authorization import (
    AuthorizationDecision,
    ExecutionAuthorizer,
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

from app.core.execution.security_adapter import (
    SecurityAuthorizationAdapter,
)


class TestCommand(BaseCommand):
    """
    Test command.
    """

    command_name = "test.security.adapter"

    def execute_name(self) -> str:
        return "test.security.adapter"


def valid_context() -> ExecutionContext:
    """
    Create a valid execution context.
    """

    return ExecutionContext(
        user_id="test-user",
        module_name="test",
        operation="security_adapter",
    )


def test_adapter_implements_authorizer_contract():
    """
    Adapter implements ExecutionAuthorizer.
    """

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: True
    )

    assert isinstance(
        adapter,
        ExecutionAuthorizer,
    )


def test_adapter_accepts_boolean_allow():
    """
    True evaluator result becomes an allow decision.
    """

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: True
    )

    decision = adapter.authorize(
        TestCommand(),
        valid_context(),
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_allowed() is True


def test_adapter_accepts_boolean_deny():
    """
    False evaluator result becomes a deny decision.
    """

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: False
    )

    decision = adapter.authorize(
        TestCommand(),
        valid_context(),
    )

    assert isinstance(
        decision,
        AuthorizationDecision,
    )

    assert decision.is_denied() is True


def test_adapter_preserves_authorization_decision():
    """
    Existing AuthorizationDecision objects are
    returned unchanged.
    """

    expected = AuthorizationDecision.deny(
        reason="Permission denied.",
        metadata={
            "permission": "test.execute",
        },
    )

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: expected
    )

    decision = adapter.authorize(
        TestCommand(),
        valid_context(),
    )

    assert decision is expected
    assert decision.is_denied()
    assert decision.reason == (
        "Permission denied."
    )
    assert decision.metadata[
        "permission"
    ] == "test.execute"


def test_adapter_rejects_invalid_evaluator():
    """
    The adapter requires a callable evaluator.
    """

    with pytest.raises(
        ExecutionContractException
    ):
        SecurityAuthorizationAdapter(
            object()
        )


def test_adapter_rejects_invalid_command():
    """
    Invalid commands are rejected.
    """

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: True
    )

    with pytest.raises(
        ExecutionContractException
    ):
        adapter.authorize(
            object(),
            valid_context(),
        )


def test_adapter_rejects_invalid_context():
    """
    Invalid contexts are rejected.
    """

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: True
    )

    with pytest.raises(
        ExecutionContractException
    ):
        adapter.authorize(
            TestCommand(),
            object(),
        )


def test_adapter_rejects_invalid_evaluator_result():
    """
    Unsupported evaluator results are rejected.
    """

    adapter = SecurityAuthorizationAdapter(
        lambda command, context: "allowed"
    )

    with pytest.raises(
        ExecutionContractException
    ):
        adapter.authorize(
            TestCommand(),
            valid_context(),
        )


def test_adapter_wraps_evaluator_failure():
    """
    Evaluator exceptions are converted to an
    execution contract exception.
    """

    def broken_evaluator(
        command,
        context,
    ):
        raise RuntimeError(
            "Security engine failure."
        )

    adapter = SecurityAuthorizationAdapter(
        broken_evaluator
    )

    with pytest.raises(
        ExecutionContractException
    ) as exc_info:

        adapter.authorize(
            TestCommand(),
            valid_context(),
        )

    assert (
        "Security authorization evaluation failed."
        in str(exc_info.value)
    )
