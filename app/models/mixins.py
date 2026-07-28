"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reusable Model Mixins
"""

from datetime import datetime

from app.extensions import db


class TimestampMixin:
    """
    Automatically tracks when a record is created and updated.
    """

    __abstract__ = True

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class AuditMixin:
    """
    Tracks who created and last modified a record.

    Foreign key relationships will be added after the
    User model is implemented.
    """

    __abstract__ = True

    created_by = db.Column(
        db.Integer,
        nullable=True,
    )

    updated_by = db.Column(
        db.Integer,
        nullable=True,
    )


class SoftDeleteMixin:
    """
    Enables soft deletion of records.
    """

    __abstract__ = True

    is_deleted = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    deleted_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    def soft_delete(self):
        """
        Mark the record as deleted without removing it.
        """

        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """
        Restore a soft-deleted record.
        """

        self.is_deleted = False
        self.deleted_at = None
