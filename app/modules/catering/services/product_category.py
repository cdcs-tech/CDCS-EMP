"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product category service.
"""

from __future__ import annotations

from app.core.crud import CRUDService

from app.modules.catering.models import ProductCategory
from app.modules.catering.repositories import ProductCategoryRepository


class ProductCategoryService(
    CRUDService[ProductCategory],
):
    """
    Application service for Catering ProductCategory entities.

    Provides the standard enterprise CRUD service boundary
    while leaving ProductCategory-specific business rules
    available for future extension.
    """

    def __init__(
        self,
        repository: ProductCategoryRepository | None = None,
    ) -> None:
        """
        Initialize the ProductCategory service.

        Args:
            repository:
                Optional ProductCategory repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or ProductCategoryRepository(),
            entity_name="ProductCategory",
        )


__all__ = [
    "ProductCategoryService",
]
