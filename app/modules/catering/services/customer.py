"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Customer service.
"""

from __future__ import annotations

from app.core.crud import CRUDService
from app.core.data import PaginatedResult, QueryOptions

from app.modules.catering.models import Customer
from app.modules.catering.repositories import CustomerRepository


class CustomerService(
    CRUDService[Customer],
):
    """
    Application service for Catering Customer entities.

    Provides the standard enterprise CRUD service boundary,
    pagination support, and Customer-specific lifecycle
    operations.
    """

    def __init__(
        self,
        repository: CustomerRepository | None = None,
    ) -> None:
        """
        Initialize the Customer service.

        Args:
            repository:
                Optional Customer repository. A default
                repository is created when one is not supplied.
        """

        super().__init__(
            repository
            or CustomerRepository(),
            entity_name="Customer",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[Customer]:
        """
        Return a paginated Customer result.

        Args:
            options:
                Query, filtering, sorting, and pagination options.

        Returns:
            A paginated Customer result.
        """

        return self.repository.paginate(
            options
        )

    def activate(
        self,
        entity_id,
    ) -> Customer:
        """
        Activate a Customer entity.

        Args:
            entity_id:
                Identifier of the Customer to activate.

        Returns:
            The activated Customer entity.

        Raises:
            EntityNotFoundException:
                When the Customer does not exist.
        """

        customer = self.get(
            entity_id
        )

        customer.status = "ACTIVE"

        return self.update(
            customer
        )

    def deactivate(
        self,
        entity_id,
    ) -> Customer:
        """
        Deactivate a Customer entity.

        Args:
            entity_id:
                Identifier of the Customer to deactivate.

        Returns:
            The deactivated Customer entity.

        Raises:
            EntityNotFoundException:
                When the Customer does not exist.
        """

        customer = self.get(
            entity_id
        )

        customer.status = "INACTIVE"

        return self.update(
            customer
        )


__all__ = [
    "CustomerService",
]
