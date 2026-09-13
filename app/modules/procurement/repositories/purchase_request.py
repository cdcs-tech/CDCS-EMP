"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Request repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.procurement.models import (
    PurchaseRequest,
)


class PurchaseRequestRepository(
    SQLAlchemyRepository[PurchaseRequest],
):
    """
    Database repository for Purchase Request entities.
    """

    def __init__(self) -> None:
        super().__init__(
            PurchaseRequest
        )


__all__ = [
    "PurchaseRequestRepository",
]
