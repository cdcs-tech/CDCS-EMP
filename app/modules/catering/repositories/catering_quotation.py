"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Quotation Repository
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.catering.models import CateringQuotation


class CateringQuotationRepository(
    SQLAlchemyRepository[CateringQuotation],
):
    """Repository for Catering Quotation persistence."""

    def __init__(self) -> None:
        super().__init__(CateringQuotation)


__all__ = [
    "CateringQuotationRepository",
]
