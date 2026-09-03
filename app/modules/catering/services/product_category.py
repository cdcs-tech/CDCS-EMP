"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product category service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import ProductCategory
from app.modules.catering.repositories import ProductCategoryRepository


class ProductCategoryService(
    CRUDService[ProductCategory],
):
    """
    Application service for Catering ProductCategory entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and ProductCategory-specific lifecycle
    operations.
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

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[ProductCategory]:
        """
        Return a paginated ProductCategory result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated ProductCategory result.
        """

        return self.repository.paginate(
            options
        )

    def activate(
        self,
        entity_id,
    ) -> ProductCategory:
        """
        Activate a ProductCategory entity.

        Args:
            entity_id:
                Identifier of the ProductCategory to activate.

        Returns:
            The activated ProductCategory entity.

        Raises:
            EntityNotFoundException:
                When the ProductCategory does not exist.
        """

        category = self.get(
            entity_id
        )

        category.is_active = True

        return self.update(
            category
        )

    def deactivate(
        self,
        entity_id,
    ) -> ProductCategory:
        """
        Deactivate a ProductCategory entity.

        Args:
            entity_id:
                Identifier of the ProductCategory to deactivate.

        Returns:
            The deactivated ProductCategory entity.

        Raises:
            EntityNotFoundException:
                When the ProductCategory does not exist.
        """

        category = self.get(
            entity_id
        )

        category.is_active = False

        return self.update(
            category
        )


__all__ = [
    "ProductCategoryService",
]
