"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase order line repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.procurement.models import PurchaseOrderLine


class PurchaseOrderLineRepository(
    SQLAlchemyRepository[PurchaseOrderLine]
):
    """
    Repository for Purchase Order Line persistence.
    """

    def __init__(self) -> None:
        super().__init__(PurchaseOrderLine)


__all__ = [
    "PurchaseOrderLineRepository",
]
