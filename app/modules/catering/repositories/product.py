"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import Product


class ProductRepository(
    SQLAlchemyRepository[Product],
):
    """
    Repository for Catering Product entities.

    Provides persistence and Product-specific retrieval
    operations without owning Product business rules.
    """

    def __init__(self) -> None:
        """
        Initialize the Product repository.
        """

        super().__init__(
            Product
        )

    def get_by_code(
        self,
        code: str,
    ) -> Optional[Product]:
        """
        Retrieve the Product associated with a business code.
        """

        if not isinstance(code, str) or not code.strip():
            return None

        statement = select(
            Product
        ).where(
            Product.code == code.strip()
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def exists_for_code(
        self,
        code: str,
    ) -> bool:
        """
        Determine whether a Product exists for the supplied
        business code.
        """

        return (
            self.get_by_code(
                code
            )
            is not None
        )
