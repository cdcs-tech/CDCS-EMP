"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration

Inventory receipt integration provider.
"""

from __future__ import annotations

from typing import Any

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.core.integration.providers.base import (
    BaseIntegrationProvider,
)
from app.modules.catering.models import StockMovement
from app.modules.catering.repositories import (
    InventoryLocationRepository,
    ProductRepository,
    StockItemRepository,
)
from app.modules.catering.services import (
    StockMovementService,
)
from app.modules.procurement.integration import (
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)


class InventoryReceiptIntegrationProvider(
    BaseIntegrationProvider,
):
    """
    Adapt Procurement receipt requests to the
    authoritative Inventory posting service.

    The provider resolves Inventory-owned references,
    constructs a draft RECEIPT movement, and delegates
    physical stock posting to StockMovementService.

    Authorization, transaction handling, StockBalance
    mutation, and StockMovement lifecycle rules remain
    owned by the Inventory service boundary.
    """

    def __init__(
        self,
        *,
        product_repository: ProductRepository | None = None,
        stock_item_repository: StockItemRepository | None = None,
        location_repository: InventoryLocationRepository | None = None,
        movement_service: StockMovementService | None = None,
    ) -> None:
        self.product_repository = (
            product_repository
            or ProductRepository()
        )
        self.stock_item_repository = (
            stock_item_repository
            or StockItemRepository()
        )
        self.location_repository = (
            location_repository
            or InventoryLocationRepository()
        )
        self.movement_service = movement_service

    @property
    def provider_name(self) -> str:
        """Return the enterprise provider name."""

        return "inventory"

    def supports(
        self,
        operation: str,
    ) -> bool:
        """Return whether this provider supports the operation."""

        return (
            operation
            == INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        )

    def validate(
        self,
        request: IntegrationRequest,
    ) -> None:
        """
        Validate the enterprise request and domain payload.
        """

        super().validate(request)

        if not self.supports(request.operation):
            raise ValueError(
                "Unsupported Inventory integration operation."
            )

        if not isinstance(
            request.payload,
            PurchaseOrderReceiptRequest,
        ):
            raise TypeError(
                "Inventory receipt integration payload must be "
                "a PurchaseOrderReceiptRequest."
            )

        if self.movement_service is None:
            raise RuntimeError(
                "Inventory movement service is required."
            )

    def execute(
        self,
        request: IntegrationRequest,
    ) -> IntegrationResponse:
        """
        Resolve Inventory references and delegate the
        receipt posting to StockMovementService.
        """

        try:
            self.validate(request)
        except (TypeError, ValueError, RuntimeError) as exc:
            return IntegrationResponse(
                success=False,
                message=str(exc),
                error="INVALID_INVENTORY_RECEIPT_REQUEST",
                request_id=request.request_id,
            )

        receipt = request.payload

        product = self.product_repository.get_by_code(
            receipt.stock_item_reference
        )

        if product is None:
            return IntegrationResponse(
                success=False,
                message=(
                    "The referenced Inventory product "
                    "could not be found."
                ),
                error="INVENTORY_PRODUCT_NOT_FOUND",
                request_id=request.request_id,
            )

        stock_item = (
            self.stock_item_repository
            .get_by_product_id(
                product.id
            )
        )

        if stock_item is None:
            return IntegrationResponse(
                success=False,
                message=(
                    "The referenced Inventory StockItem "
                    "could not be found."
                ),
                error="INVENTORY_STOCK_ITEM_NOT_FOUND",
                request_id=request.request_id,
            )

        location = (
            self.location_repository
            .get_by_code(
                receipt.inventory_location_reference
            )
        )

        if location is None:
            return IntegrationResponse(
                success=False,
                message=(
                    "The referenced Inventory location "
                    "could not be found."
                ),
                error="INVENTORY_LOCATION_NOT_FOUND",
                request_id=request.request_id,
            )

        movement = StockMovement(
            stock_item_id=stock_item.id,
            location_id=location.id,
            movement_type="RECEIPT",
            quantity=receipt.quantity_received,
            reference=receipt.receiving_reference,
            reason=(
                "Purchase Order receipt "
                f"{receipt.purchase_order_reference} / "
                f"{receipt.purchase_order_line_reference}"
            ),
            status="DRAFT",
            occurred_at=receipt.received_at,
        )

        subject = request.metadata.get(
            "subject"
        )

        try:
            posted_movement = (
                self.movement_service.post_movement(
                    movement,
                    subject=subject,
                )
            )
        except Exception as exc:
            return IntegrationResponse(
                success=False,
                message=(
                    "Inventory receipt posting could not "
                    "be completed."
                ),
                error=str(exc),
                request_id=request.request_id,
            )

        return IntegrationResponse(
            success=True,
            message=(
                "Inventory receipt posted successfully."
            ),
            data={
                "stock_movement_id": posted_movement.id,
                "stock_item_id": posted_movement.stock_item_id,
                "location_id": posted_movement.location_id,
                "quantity": posted_movement.quantity,
                "movement_type": posted_movement.movement_type,
                "status": posted_movement.status,
                "receiving_reference": (
                    receipt.receiving_reference
                ),
            },
            request_id=request.request_id,
        )
