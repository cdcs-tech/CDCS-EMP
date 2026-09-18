"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order service.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.core.data import (
    PaginatedResult,
    QueryOptions,
)
from app.modules.procurement.models import PurchaseOrder
from app.modules.procurement.repositories import (
    PurchaseOrderRepository,
)


class PurchaseOrderService(
    CRUDService[PurchaseOrder],
):
    """
    Business service for Purchase Order entities.

    Workflow lifecycle transitions are intentionally
    outside this service and belong to the dedicated
    Procurement Workflow stage.
    """

    def __init__(
        self,
        repository: PurchaseOrderRepository | None = None,
    ) -> None:
        super().__init__(
            repository or PurchaseOrderRepository(),
            entity_name="Purchase Order",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[PurchaseOrder]:
        return self.repository.paginate(options)


__all__ = [
    "PurchaseOrderService",
]
