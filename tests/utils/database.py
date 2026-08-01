"""
Database Test Helpers
"""

from app.extensions import db


def commit():
    """
    Commit current transaction.
    """
    db.session.commit()


def rollback():
    """
    Roll back current transaction.
    """
    db.session.rollback()


def flush():
    """
    Flush pending SQL statements.
    """
    db.session.flush()


def clear():
    """
    Remove current SQLAlchemy session.
    """
    db.session.remove()
