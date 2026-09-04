"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock movement repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import StockMovement


class StockMovementRepository(
    SQLAlchemyRepository[StockMovement],
):
    """
    Repository for Catering StockMovement entities.

    Provides persistence and historical retrieval operations.

    Movement posting, immutability rules, balance updates,
    and inventory business rules remain in the service layer.
    """

    def __init__(self) -> None:
        """
        Initialize the StockMovement repository.
        """

        super().__init__(
            StockMovement
        )

    def get_by_reference(
        self,
        reference: str,
    ) -> Optional[StockMovement]:
        """
        Retrieve a stock movement by its reference.
        """

        statement = select(
            StockMovement
        ).where(
            StockMovement.reference == reference
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "StockMovementRepository",
]
