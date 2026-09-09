"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Transaction management foundation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator

from app.extensions import db


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

    Used for framework testing.
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


class SQLAlchemyTransactionManager(
    TransactionManager
):
    """
    SQLAlchemy-backed transaction manager.

    Owns the lifecycle of a transaction created
    through the Flask-SQLAlchemy session.
    """

    def __init__(self):
        self.active = False

    def begin(self) -> None:
        """
        Begin or adopt a SQLAlchemy transaction.

        A transaction explicitly started by another owner is
        rejected. An incidental SQLAlchemy AUTOBEGIN transaction
        may be adopted so the enterprise transaction manager can
        take ownership of the current unit of work.
        """

        session = db.session()

        if session.in_transaction():

            transaction = session.get_transaction()

            if transaction is None:
                raise RuntimeError(
                    "A SQLAlchemy transaction is already active."
                )

            if transaction.origin.name != "AUTOBEGIN":
                raise RuntimeError(
                    "A SQLAlchemy transaction is already active."
                )

            self.active = True
            return

        session.begin()

        self.active = True

    def commit(self) -> None:
        """
        Commit the active SQLAlchemy transaction.
        """

        if not self.active:
            raise RuntimeError(
                "No active SQLAlchemy transaction."
        )

        db.session.commit()

        self.active = False

    def rollback(self) -> None:
        """
        Roll back the active SQLAlchemy transaction.
        """

        if not self.active:
            raise RuntimeError(
                "No active SQLAlchemy transaction."
            )

        try:
            db.session.rollback()
        finally:
            self.active = False
