"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase request line repository.
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.procurement.models import PurchaseRequestLine


class PurchaseRequestLineRepository(
    SQLAlchemyRepository[PurchaseRequestLine]
):
    """
    Repository for Purchase Request Line persistence.
    """

    def __init__(self) -> None:
        super().__init__(PurchaseRequestLine)
