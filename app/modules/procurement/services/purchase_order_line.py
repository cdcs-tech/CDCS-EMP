"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase order line service.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.modules.procurement.models import PurchaseOrderLine
from app.modules.procurement.repositories import (
    PurchaseOrderLineRepository,
)


class PurchaseOrderLineService(
    CRUDService[PurchaseOrderLine]
):
    """
    Service for Purchase Order Line CRUD operations.

    Workflow lifecycle transitions are intentionally
    outside this service and belong to the dedicated
    Procurement Workflow stage.
    """

    def __init__(
        self,
        repository: PurchaseOrderLineRepository | None = None,
    ) -> None:
        super().__init__(
            repository=repository
            or PurchaseOrderLineRepository(),
            entity_name="PurchaseOrderLine",
        )


__all__ = [
    "PurchaseOrderLineService",
]
