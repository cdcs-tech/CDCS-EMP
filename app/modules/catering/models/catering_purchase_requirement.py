from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin


class CateringPurchaseRequirement(
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    BaseModel,
):
    """
    Catering-owned procurement requirement derived from an EventRequirement.

    This record identifies an EventRequirement that requires procurement.
    Procurement remains authoritative for the Procurement PurchaseRequirement
    and all downstream procurement lifecycle operations.
    """

    __tablename__ = "catering_purchase_requirements"

    event_requirement_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "catering_event_requirements.id",
        ),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.String(500),
        nullable=False,
    )

    item_reference = db.Column(
        db.String(100),
        nullable=True,
    )

    quantity = db.Column(
        db.Numeric(18, 3),
        nullable=False,
    )

    unit = db.Column(
        db.String(50),
        nullable=False,
    )

    required_by_date = db.Column(
        db.Date,
        nullable=True,
    )

    justification = db.Column(
        db.String(1000),
        nullable=True,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT",
    )

    procurement_reference = db.Column(
        db.String(100),
        nullable=True,
    )

    event_requirement = db.relationship(
        "EventRequirement",
        back_populates="purchase_requirement",
        lazy="select",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantity > 0",
            name="ck_catering_purchase_requirements_quantity",
        ),
        db.CheckConstraint(
            "status IN ('DRAFT')",
            name="ck_catering_purchase_requirements_status",
        ),
    )
