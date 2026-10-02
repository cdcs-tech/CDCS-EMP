"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Revenue Domain Model
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class FinanceRevenue(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Represents a Finance-owned financial revenue record.

    The record is distinct from the originating business revenue
    fact and stores the Finance representation of that contribution.

    Source and contribution identities are represented through
    business identifiers. No cross-module foreign keys are used.

    Finance lifecycle semantics are introduced by the Finance
    Revenue Lifecycle capability.
    """

    __tablename__ = "finance_revenues"

    revenue_reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    contribution_reference = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    source_type = db.Column(
        db.String(50),
        nullable=False,
    )

    source_reference = db.Column(
        db.String(100),
        nullable=False,
    )

    amount = db.Column(
        db.Numeric(18, 2),
        nullable=False,
    )

    currency = db.Column(
        db.String(3),
        nullable=False,
    )

    revenue_date = db.Column(
        db.Date,
        nullable=False,
    )

    revenue_classification = db.Column(
        db.String(100),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
    )


__all__ = [
    "FinanceRevenue",
]
