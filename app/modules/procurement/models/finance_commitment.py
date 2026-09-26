"""
Procurement Finance Commitment Model

Represents the durable Procurement-owned intent to deliver an
approved Purchase Order's financial effect to Finance.
"""

from __future__ import annotations

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class ProcurementFinanceCommitment(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Durable Finance commitment for an approved Purchase Order.

    The commitment represents the business operation that must be
    delivered to Finance. Actual Finance delivery remains a
    post-commit integration concern.

    ``idempotency_key`` identifies the underlying business operation,
    while ``IntegrationRequest.request_id`` identifies an individual
    delivery attempt.
    """

    __tablename__ = "procurement_finance_commitments"

    purchase_order_id = db.Column(
        db.Integer,
        db.ForeignKey("purchase_orders.id"),
        nullable=False,
        unique=True,
    )

    purchase_order_reference = db.Column(
        db.String(100),
        nullable=False,
    )

    idempotency_key = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="PENDING",
    )

    attempt_count = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

    last_attempted_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    committed_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    last_failure_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    next_retry_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    last_error = db.Column(
        db.Text,
        nullable=True,
    )

    last_response_message = db.Column(
        db.Text,
        nullable=True,
    )

    last_response_status_code = db.Column(
        db.Integer,
        nullable=True,
    )

    purchase_order = db.relationship(
        "PurchaseOrder",
        lazy="select",
    )


__all__ = ["ProcurementFinanceCommitment"]
