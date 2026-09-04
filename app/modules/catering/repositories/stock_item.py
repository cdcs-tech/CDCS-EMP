"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock item repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import StockItem


class StockItemRepository(
    SQLAlchemyRepository[StockItem],
):
    """
    Repository for Catering Inventory StockItem entities.

    Provides persistence and StockItem-specific retrieval
    operations without owning inventory business rules.
    """

    def __init__(self) -> None:
        """
        Initialize the StockItem repository.
        """

        super().__init__(
            StockItem
        )

    def get_by_product_id(
        self,
        product_id: int,
    ) -> Optional[StockItem]:
        """
        Retrieve the StockItem associated with a Product.
        """

        statement = select(
            StockItem
        ).where(
            StockItem.product_id == product_id
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def exists_for_product(
        self,
        product_id: int,
    ) -> bool:
        """
        Determine whether a StockItem already exists
        for the supplied Product.
        """

        return (
            self.get_by_product_id(
                product_id
            )
            is not None
        )


__all__ = [
    "StockItemRepository",
]
