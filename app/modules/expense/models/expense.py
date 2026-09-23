"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Module

Expense operational domain model.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class Expense(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents an operational expense record managed by the
    Expense Management capability.

    Financial transactions, accounting treatment, payments,
    invoices, and other financial effects are outside this
    model's ownership boundary.
    """

    __tablename__ = "expenses"

    classification_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "expense_classifications.id",
        ),
        nullable=False,
    )

    description = db.Column(
        db.String(500),
        nullable=False,
    )

    amount = db.Column(
        db.Numeric(18, 2),
        nullable=False,
    )

    expense_date = db.Column(
        db.Date,
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    classification = db.relationship(
        "ExpenseClassification",
        back_populates="expenses",
        lazy="select",
    )


__all__ = [
    "Expense",
]
