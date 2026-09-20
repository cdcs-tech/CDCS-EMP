"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory receipt idempotency repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models.inventory_receipt_idempotency import (
    InventoryReceiptIdempotency,
)


class InventoryReceiptIdempotencyRepository(
    SQLAlchemyRepository[InventoryReceiptIdempotency],
):
    """
    Repository for Inventory receipt idempotency records.

    Persistence remains repository-owned. Idempotency business
    behavior and transaction coordination remain service-owned.
    """

    def __init__(self) -> None:
        """
        Initialize the Inventory receipt idempotency repository.
        """

        super().__init__(
            InventoryReceiptIdempotency
        )

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> Optional[InventoryReceiptIdempotency]:
        """
        Retrieve an idempotency record by its unique key.
        """

        statement = select(
            InventoryReceiptIdempotency
        ).where(
            InventoryReceiptIdempotency.idempotency_key
            == idempotency_key
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "InventoryReceiptIdempotencyRepository",
]
