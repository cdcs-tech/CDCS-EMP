"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Expense Cost Integration

Catering-owned association and consumption state for
approved Expense records that are explicitly eligible
to contribute to Catering.
"""

from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class CateringExpenseCostAssociation(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Catering-owned association for an Expense that is
    explicitly eligible for Catering cost consumption.

    The Expense record remains owned by the Expense module.
    This model stores only the Catering-side association
    and consumption state.

    No foreign key to the Expense module is intentionally
    defined. The expense_id is an external business
    identifier communicated across the enterprise
    integration boundary.
    """

    __tablename__ = "catering_expense_cost_associations"

    expense_id = db.Column(
        db.Integer,
        nullable=False,
    )

    catering_context_type = db.Column(
        db.String(50),
        nullable=False,
    )

    catering_context_reference = db.Column(
        db.String(255),
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ELIGIBLE",
    )

    contribution_id = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )

    consumed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        db.UniqueConstraint(
            "expense_id",
            "catering_context_type",
            "catering_context_reference",
            name=(
                "uq_catering_expense_cost_association_context"
            ),
        ),
    )

    def mark_consumed(
        self,
        consumed_at: datetime,
    ) -> None:
        """
        Mark the Catering association as consumed.

        The caller is responsible for ensuring that the
        originating Expense is approved and eligible before
        applying this state change.
        """

        if self.status == "CONSUMED":
            return

        self.status = "CONSUMED"
        self.consumed_at = consumed_at


__all__ = [
    "CateringExpenseCostAssociation",
]
