"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product category repository.
"""

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.catering.models import (
    ProductCategory,
)


class ProductCategoryRepository(
    SQLAlchemyRepository[ProductCategory],
):
    """
    Repository for Catering ProductCategory entities.
    """

    def __init__(self) -> None:
        """
        Initialize the ProductCategory repository.
        """

        super().__init__(
            ProductCategory
        )


__all__ = [
    "ProductCategoryRepository",
]
