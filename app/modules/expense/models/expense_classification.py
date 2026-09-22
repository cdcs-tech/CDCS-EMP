"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense classification master-data model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class ExpenseClassification(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a reusable classification of expenses managed by
    the Expense Management capability.
    """

    __tablename__ = "expense_classifications"

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    code = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.String(500),
        nullable=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    expenses = db.relationship(
        "Expense",
        back_populates="classification",
        lazy="select",
    )


__all__ = [
    "ExpenseClassification",
]
