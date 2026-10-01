"""
Post-commit coordinator tests.
"""

from unittest.mock import MagicMock

import pytest

from app.core.execution import (
    ExecutionContext,
    ExecutionResult,
    PostCommitCoordinator,
    PostCommitExecutor,
)


def build_context() -> ExecutionContext:

    return ExecutionContext(
        user_id="user-001",
        operation="test.operation",
    )


def build_result() -> ExecutionResult:

    return ExecutionResult.success_result(
        data={
            "completed": True,
        }
    )


def test_coordinator_creation_without_executors():

    coordinator = PostCommitCoordinator()

    assert (
        coordinator.executors()
        == ()
    )


def test_coordinator_registers_executor():

    executor = MagicMock(
        spec=PostCommitExecutor
    )

    coordinator = PostCommitCoordinator()

    coordinator.register(
        executor
    )

    assert coordinator.executors() == (
        executor,
    )


def test_coordinator_rejects_invalid_executor():

    coordinator = PostCommitCoordinator()

    with pytest.raises(
        TypeError,
        match="Post-commit executor",
    ):
        coordinator.register(
            object()
        )


def test_coordinator_accepts_initial_executors():

    first = MagicMock(
        spec=PostCommitExecutor
    )

    second = MagicMock(
        spec=PostCommitExecutor
    )

    coordinator = PostCommitCoordinator(
        executors=[
            first,
            second,
        ]
    )

    assert coordinator.executors() == (
        first,
        second,
    )


def test_coordinator_executes_executors_in_registration_order():

    calls = []

    first = MagicMock(
        spec=PostCommitExecutor
    )

    second = MagicMock(
        spec=PostCommitExecutor
    )

    def first_execute(
        command,
        context,
        result,
    ):

        calls.append(
            "first"
        )

    def second_execute(
        command,
        context,
        result,
    ):

        calls.append(
            "second"
        )

    first.execute.side_effect = (
        first_execute
    )

    second.execute.side_effect = (
        second_execute
    )

    coordinator = PostCommitCoordinator(
        executors=[
            first,
            second,
        ]
    )

    command = object()
    context = build_context()
    result = build_result()

    coordinator.execute(
        command,
        context,
        result,
    )

    assert calls == [
        "first",
        "second",
    ]

    first.execute.assert_called_once_with(
        command,
        context,
        result,
    )

    second.execute.assert_called_once_with(
        command,
        context,
        result,
    )


def test_coordinator_propagates_executor_failure():

    first = MagicMock(
        spec=PostCommitExecutor
    )

    second = MagicMock(
        spec=PostCommitExecutor
    )

    first.execute.side_effect = RuntimeError(
        "Post-commit failure."
    )

    coordinator = PostCommitCoordinator(
        executors=[
            first,
            second,
        ]
    )

    with pytest.raises(
        RuntimeError,
        match="Post-commit failure",
    ):

        coordinator.execute(
            object(),
            build_context(),
            build_result(),
        )

    first.execute.assert_called_once()

    second.execute.assert_not_called()
