"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Request service.
"""

from __future__ import annotations

from app.core.crud.service import (
    CRUDService,
)

from app.core.data import (
    PaginatedResult,
    QueryOptions,
)

from app.modules.procurement.models import (
    PurchaseRequest,
)

from app.modules.procurement.repositories import (
    PurchaseRequestRepository,
)


class PurchaseRequestService(
    CRUDService[PurchaseRequest],
):
    """
    Business service for Purchase Request entities.

    Workflow-specific lifecycle execution remains owned
    by the Procurement workflow handlers and enterprise
    execution dispatcher.
    """

    def __init__(
        self,
        repository: PurchaseRequestRepository | None = None,
    ) -> None:
        super().__init__(
            repository
            or PurchaseRequestRepository(),
            entity_name="Purchase Request",
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[PurchaseRequest]:
        """
        Return a paginated Purchase Request result.
        """

        return self.repository.paginate(
            options
        )


__all__ = [
    "PurchaseRequestService",
]
