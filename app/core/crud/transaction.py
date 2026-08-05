"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Transaction management foundation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator


class TransactionManager(
    ABC
):
    """
    Abstract transaction manager.

    Defines the standard transaction
    lifecycle used by enterprise services.
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
        Commit current transaction.
        """

        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback current transaction.
        """

        raise NotImplementedError

    @contextmanager
    def transaction(
        self,
    ) -> Iterator[None]:
        """
        Transaction context manager.

        Automatically commits on success
        and rolls back on failure.
        """

        self.begin()

        try:

            yield

            self.commit()

        except Exception:

            self.rollback()

            raise


class SimpleTransactionManager(
    TransactionManager
):
    """
    Basic transaction manager implementation.

    Used for framework testing until the
    SQLAlchemy transaction layer is introduced.
    """

    def __init__(self):

        self.active = False

        self.committed = False

        self.rolled_back = False


    def begin(self) -> None:
        """
        Start transaction.
        """

        self.active = True

        self.committed = False

        self.rolled_back = False


    def commit(self) -> None:
        """
        Commit transaction.
        """

        self.active = False

        self.committed = True


    def rollback(self) -> None:
        """
        Rollback transaction.
        """

        self.active = False

        self.rolled_back = True
