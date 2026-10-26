"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Purchase Order line service.
"""

from __future__ import annotations

from sqlalchemy import select

from app.core.crud.service import CRUDService
from app.extensions import db
from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseOrderLine,
)
from app.modules.procurement.repositories import (
    PurchaseOrderLineRepository,
)
from app.modules.procurement.workflows import (
    PurchaseOrderWorkflow,
)


class PurchaseOrderLineService(
    CRUDService[PurchaseOrderLine]
):
    """
    Service for Purchase Order Line CRUD operations.

    Commercial line changes are allowed only while the
    parent Purchase Order's persisted state is DRAFT.
    """

    def __init__(
        self,
        repository: PurchaseOrderLineRepository | None = None,
    ) -> None:
        super().__init__(
            repository=repository
            or PurchaseOrderLineRepository(),
            entity_name="PurchaseOrderLine",
        )

    def get_by_guid(
        self,
        guid: str,
    ) -> PurchaseOrderLine | None:
        """Retrieve a Purchase Order line by its persisted GUID."""

        if not isinstance(guid, str) or not guid.strip():
            return None

        statement = select(
            PurchaseOrderLine
        ).where(
            PurchaseOrderLine.guid == guid.strip()
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def _get_persisted_purchase_order_status(
        self,
        purchase_order_id: int,
    ) -> str | None:
        """Read the parent's persisted state from the database."""

        statement = select(
            PurchaseOrder.status
        ).where(
            PurchaseOrder.id == purchase_order_id
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()

    def _require_draft_parent(
        self,
        purchase_order_id: int,
        operation: str,
    ) -> None:
        """Reject line mutations when the parent PO is not DRAFT."""

        persisted_status = (
            self._get_persisted_purchase_order_status(
                purchase_order_id
            )
        )

        if persisted_status is None:
            raise ValueError(
                "Parent Purchase Order does not exist."
            )

        if persisted_status != PurchaseOrderWorkflow.DRAFT:
            raise ValueError(
                f"Cannot {operation} a Purchase Order line "
                f"unless its parent Purchase Order's "
                f"persisted status is DRAFT."
            )

    def create(
        self,
        entity: PurchaseOrderLine,
    ) -> PurchaseOrderLine:
        """Create a line only under a persisted DRAFT order."""

        self._require_draft_parent(
            entity.purchase_order_id,
            "create",
        )

        return self.repository.add(
            entity
        )

    def update(
        self,
        entity: PurchaseOrderLine,
    ) -> PurchaseOrderLine:
        """Update a line only under its original DRAFT parent."""

        persisted_line = self.get(
            entity.id
        )

        original_parent_id = (
            persisted_line.purchase_order_id
        )

        if entity.purchase_order_id != original_parent_id:
            raise ValueError(
                "Purchase Order line reassignment is not permitted "
                "through generic updates."
            )

        self._require_draft_parent(
            original_parent_id,
            "update",
        )

        return self.repository.update(
            entity
        )

    def delete(
        self,
        entity_id,
    ) -> None:
        """Delete a line only while its parent PO is DRAFT."""

        entity = self.get(
            entity_id
        )

        self._require_draft_parent(
            entity.purchase_order_id,
            "delete",
        )

        self.repository.delete(
            entity
        )


__all__ = [
    "PurchaseOrderLineService",
]
