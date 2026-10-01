"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Expense Cost Association service.
"""

from __future__ import annotations

from app.modules.catering.models import CateringExpenseCostAssociation
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)


class CateringExpenseCostAssociationService:
    """
    Application service for explicit Catering Expense Cost Associations.

    The association is Catering-owned and identifies an Expense as
    eligible to contribute to a specified Catering context.

    This service deliberately does not:
    - access the Expense module;
    - verify Expense approval;
    - modify Expense records;
    - execute integration delivery;
    - consume the Expense;
    - calculate or allocate Catering costs.
    """

    CREATE_PERMISSION = (
        "CATERING.EXPENSE_COST_ASSOCIATION.CREATE"
    )

    def __init__(
        self,
        repository: (
            CateringExpenseCostAssociationRepository | None
        ) = None,
        authorization_adapter: (
            CateringAuthorizationAdapter | None
        ) = None,
    ) -> None:
        """
        Initialize the Catering Expense Cost Association service.
        """

        self.repository = (
            repository
            or CateringExpenseCostAssociationRepository()
        )
        self.authorization_adapter = authorization_adapter

    def _authorize(
        self,
        subject,
        permission_code: str,
    ) -> None:
        """
        Authorize an association operation.

        Authorization fails closed when no Catering authorization
        adapter is configured.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required"
            )

        self.authorization_adapter.authorize(
            subject,
            permission_code,
        )

    def create(
        self,
        entity: CateringExpenseCostAssociation,
        *,
        subject,
    ) -> CateringExpenseCostAssociation:
        """
        Create an explicit Catering Expense Cost Association.

        The association establishes Catering-side eligibility only.
        Expense ownership and Expense lifecycle remain outside this
        service.
        """

        self._authorize(
            subject,
            self.CREATE_PERMISSION,
        )

        return self.repository.add(
            entity,
        )


__all__ = [
    "CateringExpenseCostAssociationService",
]
