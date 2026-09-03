"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import Product
from app.modules.catering.repositories import ProductRepository


class ProductService(
    CRUDService[Product],
):
    """
    Application service for Catering Product entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and Product-specific lifecycle
    operations.
    """

    def __init__(
        self,
        repository: ProductRepository | None = None,
    ) -> None:
        """
        Initialize the Product service.

        Args:
            repository:
                Optional Product repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or ProductRepository(),
            entity_name="Product",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[Product]:
        """
        Return a paginated Product result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated Product result.
        """

        return self.repository.paginate(
            options
        )

    def activate(
        self,
        entity_id,
    ) -> Product:
        """
        Activate a Product entity.

        Args:
            entity_id:
                Identifier of the Product to activate.

        Returns:
            The activated Product entity.

        Raises:
            EntityNotFoundException:
                When the Product does not exist.
        """

        product = self.get(
            entity_id
        )

        product.is_active = True

        return self.update(
            product
        )

    def deactivate(
        self,
        entity_id,
    ) -> Product:
        """
        Deactivate a Product entity.

        Args:
            entity_id:
                Identifier of the Product to deactivate.

        Returns:
            The deactivated Product entity.

        Raises:
            EntityNotFoundException:
                When the Product does not exist.
        """

        product = self.get(
            entity_id
        )

        product.is_active = False

        return self.update(
            product
        )


__all__ = [
    "ProductService",
]
