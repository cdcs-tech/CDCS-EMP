"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Procurement Finance commitment repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.procurement.models import (
    ProcurementFinanceCommitment,
)


class ProcurementFinanceCommitmentRepository(
    SQLAlchemyRepository[ProcurementFinanceCommitment],
):
    """
    Repository for Procurement Finance commitment records.

    Persistence remains repository-owned. Commitment state
    transitions, retry behavior, and idempotency business rules
    remain service-owned.
    """

    def __init__(self) -> None:
        """
        Initialize the Procurement Finance commitment repository.
        """

        super().__init__(
            ProcurementFinanceCommitment
        )

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Optional[ProcurementFinanceCommitment]:
        """
        Retrieve a Finance commitment by its unique idempotency key.
        """

        statement = select(
            ProcurementFinanceCommitment
        ).where(
            ProcurementFinanceCommitment.idempotency_key
            == idempotency_key
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def get_by_purchase_order_id(
        self,
        purchase_order_id: int,
    ) -> Optional[ProcurementFinanceCommitment]:
        """
        Retrieve the Finance commitment associated with a
        Purchase Order.
        """

        statement = select(
            ProcurementFinanceCommitment
        ).where(
            ProcurementFinanceCommitment.purchase_order_id
            == purchase_order_id
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "ProcurementFinanceCommitmentRepository",
]
