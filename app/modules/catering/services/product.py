"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product service.
"""

from __future__ import annotations

from app.core.crud import CRUDService

from app.modules.catering.models import Product
from app.modules.catering.repositories import ProductRepository


class ProductService(
    CRUDService[Product],
):
    """
    Application service for Catering Product entities.

    Provides the standard enterprise CRUD service boundary
    while leaving Product-specific business rules available
    for future extension.
    """

    def __init__(
        self,
        repository: ProductRepository | None = None,
    ) -> None:
        """
        Initialize the Product service.

        Args:
            repository:
                Optional Product repository. A default repository
                is created when one is not supplied.
        """

        super().__init__(
            repository
            or ProductRepository(),
            entity_name="Product",
        )


__all__ = [
    "ProductService",
]
