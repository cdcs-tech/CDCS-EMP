"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Stock balance repository.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import StockBalance


class StockBalanceRepository(
    SQLAlchemyRepository[StockBalance],
):
    """
    Repository for Catering StockBalance entities.

    Provides persistence and balance retrieval operations.

    Business rules governing balance changes remain in the
    inventory service layer.
    """

    def __init__(self) -> None:
        """
        Initialize the StockBalance repository.
        """

        super().__init__(
            StockBalance
        )

    def get_by_stock_item_and_location(
        self,
        stock_item_id: int,
        location_id: int,
    ) -> Optional[StockBalance]:
        """
        Retrieve the balance for a StockItem at a Location.
        """

        statement = select(
            StockBalance
        ).where(
            StockBalance.stock_item_id == stock_item_id,
            StockBalance.location_id == location_id,
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def get_by_stock_item(
        self,
        stock_item_id: int,
    ) -> List[StockBalance]:
        """
        Retrieve all location balances for a StockItem.
        """

        statement = (
            select(
                StockBalance
            )
            .where(
                StockBalance.stock_item_id == stock_item_id
            )
            .order_by(
                StockBalance.location_id.asc()
            )
        )

        return list(
            db.session.execute(
                statement
            ).scalars().all()
        )

    def get_by_location(
        self,
        location_id: int,
    ) -> List[StockBalance]:
        """
        Retrieve all StockItem balances at a Location.
        """

        statement = (
            select(
                StockBalance
            )
            .where(
                StockBalance.location_id == location_id
            )
            .order_by(
                StockBalance.stock_item_id.asc()
            )
        )

        return list(
            db.session.execute(
                statement
            ).scalars().all()
        )


__all__ = [
    "StockBalanceRepository",
]
