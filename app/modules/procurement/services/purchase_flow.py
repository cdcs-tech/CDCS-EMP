
"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Services

Procurement purchase-flow application coordinator.

This service coordinates progression between existing Procurement
documents. It does not own Procurement workflow execution.
"""

from __future__ import annotations

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseRequest,
)
from app.modules.procurement.repositories import (
    PurchaseRequestRepository,
    PurchaseRequirementRepository,
    SupplierRepository,
)
from app.modules.procurement.services.purchase_order import (
    PurchaseOrderService,
)
from app.modules.procurement.services.purchase_request import (
    PurchaseRequestService,
)
from app.security.authorization import AuthorizationService


class ProcurementPurchaseFlowService:
    """
    Coordinate progression across the existing Procurement document chain.

    Supported progression:

        PurchaseRequirement -> PurchaseRequest
        PurchaseRequest -> PurchaseOrder

    Created documents begin in DRAFT. Workflow transitions, receiving,
    Inventory effects, and Finance integration remain outside this service.
    """

    PURCHASE_REQUEST_CREATE = "PROCUREMENT.PURCHASE_REQUEST.CREATE"
    PURCHASE_ORDER_CREATE = "PROCUREMENT.PURCHASE_ORDER.CREATE"

    def __init__(
        self,
        *,
        purchase_requirement_repository=None,
        purchase_request_repository=None,
        supplier_repository=None,
        purchase_request_service=None,
        purchase_order_service=None,
        authorization_adapter=None,
    ) -> None:
        self.purchase_requirement_repository = (
            purchase_requirement_repository
            or PurchaseRequirementRepository()
        )
        self.purchase_request_repository = (
            purchase_request_repository
            or PurchaseRequestRepository()
        )
        self.supplier_repository = (
            supplier_repository
            or SupplierRepository()
        )
        self.purchase_request_service = (
            purchase_request_service
            or PurchaseRequestService()
        )
        self.purchase_order_service = (
            purchase_order_service
            or PurchaseOrderService()
        )
        self.authorization_adapter = (
            authorization_adapter
            or CateringAuthorizationAdapter(
                AuthorizationService.authorize_execution
            )
        )

    def _authorize(self, subject, permission: str) -> None:
        """Enforce the existing Procurement execution permission."""
        self.authorization_adapter.authorize(subject, permission)

    def _get_purchase_requirement(self, purchase_requirement):
        """Resolve the existing Procurement Purchase Requirement."""
        requirement_id = getattr(purchase_requirement, "id", None)

        if requirement_id is None:
            raise EntityNotFoundException(
                "PurchaseRequirement",
                requirement_id,
            )

        source = self.purchase_requirement_repository.get_by_id(
            requirement_id,
        )

        if source is None:
            raise EntityNotFoundException(
                "PurchaseRequirement",
                requirement_id,
            )

        return source

    def _get_purchase_request(self, purchase_request):
        """Resolve the existing Procurement Purchase Request."""
        request_id = getattr(purchase_request, "id", None)

        if request_id is None:
            raise EntityNotFoundException(
                "PurchaseRequest",
                request_id,
            )

        source = self.purchase_request_repository.get_by_id(
            request_id,
        )

        if source is None:
            raise EntityNotFoundException(
                "PurchaseRequest",
                request_id,
            )

        return source

    def _validate_supplier(self, supplier_id) -> None:
        """Ensure the selected Supplier exists."""
        supplier = self.supplier_repository.get_by_id(supplier_id)

        if supplier is None:
            raise EntityNotFoundException(
                "Supplier",
                supplier_id,
            )

    def create_purchase_request_from_requirement(
        self,
        purchase_requirement,
        *,
        reference: str,
        request_date,
        required_by_date=None,
        justification=None,
        notes=None,
        subject,
    ) -> PurchaseRequest:
        """
        Create a DRAFT Purchase Request from an existing requirement.

        Only the parent document is created. Lines and workflow
        transitions remain separate operations.
        """
        self._authorize(
            subject,
            self.PURCHASE_REQUEST_CREATE,
        )

        source = self._get_purchase_requirement(
            purchase_requirement,
        )

        purchase_request = PurchaseRequest(
            reference=reference,
            purchase_requirement_id=source.id,
            request_date=request_date,
            required_by_date=required_by_date,
            status="DRAFT",
            justification=justification,
            notes=notes,
        )

        return self.purchase_request_service.create(
            purchase_request,
        )

    def create_purchase_order_from_request(
        self,
        purchase_request,
        *,
        reference: str,
        currency: str,
        supplier_id,
        order_date,
        expected_delivery_date=None,
        subject,
    ) -> PurchaseOrder:
        """
        Create a DRAFT Purchase Order from an existing request.

        Only the parent document is created. Lines and workflow
        transitions remain separate operations.
        """
        self._authorize(
            subject,
            self.PURCHASE_ORDER_CREATE,
        )

        source = self._get_purchase_request(purchase_request)
        self._validate_supplier(supplier_id)

        purchase_order = PurchaseOrder(
            reference=reference,
            currency=currency,
            supplier_id=supplier_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            status="DRAFT",
            purchase_request_id=source.id,
        )

        return self.purchase_order_service.create(
            purchase_order,
        )


__all__ = ["ProcurementPurchaseFlowService"]
