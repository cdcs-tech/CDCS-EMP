"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock transfer repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import StockTransfer


class StockTransferRepository(
    SQLAlchemyRepository[StockTransfer],
):
    """
    Repository for Catering StockTransfer entities.

    Provides persistence and transfer-specific retrieval
    operations without owning transfer business rules.
    """

    def __init__(self) -> None:
        """
        Initialize the StockTransfer repository.
        """

        super().__init__(
            StockTransfer
        )

    def get_by_reference(
        self,
        reference: str,
    ) -> Optional[StockTransfer]:
        """
        Retrieve a stock transfer by its unique reference.
        """

        statement = select(
            StockTransfer
        ).where(
            StockTransfer.reference == reference
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "StockTransferRepository",
]
