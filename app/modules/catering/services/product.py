"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Product service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.crud.exceptions import EntityValidationException
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import Product
from app.modules.catering.repositories import ProductRepository


class ProductService(
    CRUDService[Product],
):
    """
    Application service for Catering Product entities.

    Product is the authoritative owner of the unit used by
    associated Inventory stock quantities.
    """

    MAX_UNIT_LENGTH = 50

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

    @classmethod
    def _normalize_unit(
        cls,
        unit: object,
    ) -> str:
        """
        Validate and normalize the authoritative Product unit.

        Surrounding whitespace is removed. Blank, non-string,
        and overlength values are rejected before persistence.
        """

        if not isinstance(unit, str):
            raise EntityValidationException(
                "Product unit must be a non-empty string "
                "of at most 50 characters."
            )

        normalized_unit = unit.strip()

        if (
            not normalized_unit
            or len(normalized_unit) > cls.MAX_UNIT_LENGTH
        ):
            raise EntityValidationException(
                "Product unit must be a non-empty string "
                "of at most 50 characters."
            )

        return normalized_unit

    def create(
        self,
        entity: Product,
    ) -> Product:
        """
        Validate the Product unit before creating the entity.
        """

        entity.unit = self._normalize_unit(
            entity.unit
        )

        return super().create(
            entity
        )

    def update(
        self,
        entity: Product,
    ) -> Product:
        """
        Validate the Product unit before updating the entity.
        """

        entity.unit = self._normalize_unit(
            entity.unit
        )

        return super().update(
            entity
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
