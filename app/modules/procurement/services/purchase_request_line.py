"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase request line service.
"""

from __future__ import annotations

from app.core.crud.service import CRUDService
from app.modules.procurement.models import PurchaseRequestLine
from app.modules.procurement.repositories import (
    PurchaseRequestLineRepository,
)


class PurchaseRequestLineService(
    CRUDService[PurchaseRequestLine]
):
    """
    Service for Purchase Request Line CRUD operations.
    """

    def __init__(
        self,
        repository: PurchaseRequestLineRepository | None = None,
    ) -> None:
        super().__init__(
            repository=repository
            or PurchaseRequestLineRepository(),
            entity_name="PurchaseRequestLine",
        )
