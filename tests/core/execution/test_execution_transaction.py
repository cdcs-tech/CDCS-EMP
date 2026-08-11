"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.9.2

Execution transaction boundary tests.
"""

import pytest

from app.core.crud.transaction import (
    SimpleTransactionManager,
)

from app.core.execution.transaction import (
    CRUDTransactionBoundary,
    ExecutionTransactionBoundary,
)


class TestTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Test implementation of the execution
    transaction boundary.
    """

    def __init__(self):
        self.events = []

    def begin(self) -> None:
        self.events.append("begin")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")


def test_transaction_boundary_requires_lifecycle_methods():
    """
    The transaction boundary exposes the
    required lifecycle operations.
    """

    boundary = TestTransactionBoundary()

    boundary.begin()
    boundary.commit()

    assert boundary.events == [
        "begin",
        "commit",
    ]


def test_transaction_context_commits_on_success():
    """
    A successful transaction commits.
    """

    boundary = TestTransactionBoundary()

    with boundary.transaction():
        boundary.events.append("execute")

    assert boundary.events == [
        "begin",
        "execute",
        "commit",
    ]


def test_transaction_context_rolls_back_on_failure():
    """
    A failed transaction rolls back and
    preserves the original exception.
    """

    boundary = TestTransactionBoundary()

    with pytest.raises(
        RuntimeError,
        match="execution failed",
    ):
        with boundary.transaction():
            boundary.events.append("execute")
            raise RuntimeError(
                "execution failed"
            )

    assert boundary.events == [
        "begin",
        "execute",
        "rollback",
    ]


def test_crud_transaction_boundary_implements_execution_contract():
    """
    CRUDTransactionBoundary implements the
    execution transaction boundary.
    """

    manager = SimpleTransactionManager()

    boundary = CRUDTransactionBoundary(
        manager
    )

    assert isinstance(
        boundary,
        ExecutionTransactionBoundary,
    )


def test_crud_transaction_boundary_delegates_begin_and_commit():
    """
    CRUDTransactionBoundary delegates begin
    and commit to the underlying transaction
    manager.
    """

    manager = SimpleTransactionManager()

    boundary = CRUDTransactionBoundary(
        manager
    )

    with boundary.transaction():
        assert manager.active is True

    assert manager.active is False
    assert manager.committed is True
    assert manager.rolled_back is False


def test_crud_transaction_boundary_delegates_rollback():
    """
    CRUDTransactionBoundary delegates rollback
    when execution fails.
    """

    manager = SimpleTransactionManager()

    boundary = CRUDTransactionBoundary(
        manager
    )

    with pytest.raises(
        RuntimeError,
        match="transaction failed",
    ):
        with boundary.transaction():
            assert manager.active is True
            raise RuntimeError(
                "transaction failed"
            )

    assert manager.active is False
    assert manager.committed is False
    assert manager.rolled_back is True


def test_crud_transaction_boundary_rejects_invalid_manager():
    """
    CRUDTransactionBoundary rejects objects
    that do not implement TransactionManager.
    """

    with pytest.raises(
        TypeError,
        match=(
            "transaction_manager must be a "
            "TransactionManager"
        ),
    ):
        CRUDTransactionBoundary(
            object()
        )
