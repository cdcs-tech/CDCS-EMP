"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Inventory location repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import InventoryLocation


class InventoryLocationRepository(
    SQLAlchemyRepository[InventoryLocation],
):
    """
    Repository for Catering InventoryLocation entities.

    Provides persistence and location-specific retrieval
    operations without owning inventory business rules.
    """

    def __init__(self) -> None:
        """
        Initialize the InventoryLocation repository.
        """

        super().__init__(
            InventoryLocation
        )

    def get_by_code(
        self,
        code: str,
    ) -> Optional[InventoryLocation]:
        """
        Retrieve an inventory location by its unique code.
        """

        statement = select(
            InventoryLocation
        ).where(
            InventoryLocation.code == code
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "InventoryLocationRepository",
]
