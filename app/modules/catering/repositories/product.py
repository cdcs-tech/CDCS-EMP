"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.catering.models import Product


class ProductRepository(
    SQLAlchemyRepository[Product],
):
    """
    Repository for Catering Product entities.
    """

    def __init__(self) -> None:
        """
        Initialize the Product repository.
        """

        super().__init__(
            Product
        )


__all__ = [
    "ProductRepository",
]
