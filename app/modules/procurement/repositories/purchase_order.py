"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.procurement.models import (
    PurchaseOrder,
)


class PurchaseOrderRepository(
    SQLAlchemyRepository[PurchaseOrder],
):
    """
    Database repository for Purchase Order entities.
    """

    def __init__(self) -> None:
        super().__init__(
            PurchaseOrder
        )


__all__ = [
    "PurchaseOrderRepository",
]
