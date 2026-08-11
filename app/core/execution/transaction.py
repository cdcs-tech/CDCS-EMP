"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution transaction boundary.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator

from app.core.crud.transaction import (
    TransactionManager,
)

class ExecutionTransactionFailure(
    Exception
):
    """ Internal signal indicating that an execution
    transaction must be rolled back because the
    command returned a failed execution result.
    """
    def __init__(
        self,
        result,
    ) -> None:
        self.result = result
        super().__init__(
            "Execution transaction failed."
            )


class ExecutionTransactionBoundary(ABC):
    """
    Defines the transaction boundary contract
    used by enterprise command execution.

    The execution framework depends on this
    abstraction rather than directly depending
    on a concrete transaction implementation.
    """

    @abstractmethod
    def begin(self) -> None:
        """
        Begin a transaction.
        """

        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        """
        Commit the current transaction.
        """

        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """
        Roll back the current transaction.
        """

        raise NotImplementedError

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """
        Execute a block within a transaction.

        The transaction is committed when the block
        completes successfully.

        The transaction is rolled back when an
        exception is raised.
        """

        self.begin()

        try:
            yield

            self.commit()

        except Exception:
            self.rollback()
            raise


class CRUDTransactionBoundary(
    ExecutionTransactionBoundary
):
    """
    Execution transaction boundary backed by
    the existing CRUD transaction manager.

    The execution framework depends on the
    ExecutionTransactionBoundary abstraction,
    while transaction lifecycle operations are
    delegated to the CRUD TransactionManager.
    """

    def __init__(
        self,
        transaction_manager: TransactionManager,
    ) -> None:
        """
        Initialize the CRUD-backed transaction
        boundary.
        """

        if not isinstance(
            transaction_manager,
            TransactionManager,
        ):
            raise TypeError(
                "transaction_manager must be a "
                "TransactionManager."
            )

        self.transaction_manager = (
            transaction_manager
        )

    def begin(self) -> None:
        """
        Begin the underlying transaction.
        """

        self.transaction_manager.begin()

    def commit(self) -> None:
        """
        Commit the underlying transaction.
        """

        self.transaction_manager.commit()

    def rollback(self) -> None:
        """
        Roll back the underlying transaction.
        """

        self.transaction_manager.rollback()


__all__ = [
    "ExecutionTransactionBoundary",
    "CRUDTransactionBoundary",
    "ExecutionTransactionFailure"
]
