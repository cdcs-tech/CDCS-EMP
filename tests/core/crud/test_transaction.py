"""
CDCS Enterprise Management Platform (CDCS-EMP)

SQLAlchemy transaction manager tests.
"""

import pytest

from app.core.crud.transaction import (
    SQLAlchemyTransactionManager,
)
from app.extensions import db


def test_sqlalchemy_transaction_manager_begins_transaction(app):
    """
    The manager starts and owns a SQLAlchemy transaction.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        assert manager.active is False
        assert db.session().in_transaction() is False

        manager.begin()

        assert manager.active is True
        assert db.session().in_transaction() is True

        manager.rollback()

        assert manager.active is False
        assert db.session().in_transaction() is False


def test_sqlalchemy_transaction_manager_commits_transaction(app):
    """
    The manager commits its active transaction.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        manager.begin()

        assert manager.active is True

        manager.commit()

        assert manager.active is False
        assert db.session().in_transaction() is False


def test_sqlalchemy_transaction_manager_rolls_back_transaction(app):
    """
    The manager rolls back its active transaction.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        manager.begin()

        assert manager.active is True

        manager.rollback()

        assert manager.active is False
        assert db.session().in_transaction() is False


def test_sqlalchemy_transaction_context_commits(app):
    """
    The transaction context commits on success.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        with manager.transaction():

            assert manager.active is True
            assert db.session().in_transaction() is True

        assert manager.active is False
        assert db.session().in_transaction() is False


def test_sqlalchemy_transaction_context_rolls_back_on_failure(app):
    """
    The transaction context rolls back on failure.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        with pytest.raises(
            RuntimeError,
            match="transaction failed",
        ):
            with manager.transaction():

                assert manager.active is True

                raise RuntimeError(
                    "transaction failed"
                )

        assert manager.active is False
        assert db.session().in_transaction() is False


def test_sqlalchemy_transaction_manager_rejects_existing_transaction(
    app,
):
    """
    The manager refuses to take ownership of an
    already-active SQLAlchemy transaction.
    """

    with app.app_context():

        db.session.begin()

        manager = SQLAlchemyTransactionManager()

        with pytest.raises(
            RuntimeError,
            match="transaction is already active",
        ):
            manager.begin()

        db.session.rollback()


def test_sqlalchemy_transaction_manager_rejects_commit_without_transaction(
    app,
):
    """
    Commit requires an active manager-owned transaction.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        with pytest.raises(
            RuntimeError,
            match="No active SQLAlchemy transaction",
        ):
            manager.commit()


def test_sqlalchemy_transaction_manager_rejects_rollback_without_transaction(
    app,
):
    """
    Rollback requires an active manager-owned transaction.
    """

    with app.app_context():

        manager = SQLAlchemyTransactionManager()

        with pytest.raises(
            RuntimeError,
            match="No active SQLAlchemy transaction",
        ):
            manager.rollback()
