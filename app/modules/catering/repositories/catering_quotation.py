"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Quotation Repository
"""

from __future__ import annotations

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.catering.models import CateringQuotation
from app.core.data.query import QueryOptions


class CateringQuotationRepository(
    SQLAlchemyRepository[CateringQuotation],
):
    """Repository for Catering Quotation persistence."""

    def __init__(self) -> None:
        super().__init__(CateringQuotation)

    def get_accepted_by_event_id(
        self,
        event_id: int,
    ) -> CateringQuotation | None:
        """Retrieve the accepted quotation associated with an Event."""

        quotations = self.query(
            QueryOptions(
                filters={
                    "event_id": event_id,
                    "status": "ACCEPTED",
                },
                page=1,
                page_size=2,
            )
        )

        if len(quotations) > 1:
            raise ValueError(
                "Multiple ACCEPTED quotations exist for the same event."
            )

        return quotations[0] if quotations else None


__all__ = [
    "CateringQuotationRepository",
]
