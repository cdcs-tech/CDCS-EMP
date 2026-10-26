"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration

Inventory receipt integration provider.
"""

from __future__ import annotations

from decimal import Decimal

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
    INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION,
    InventoryReceiptStatusQueryResult,
    PurchaseOrderLineReceiptStatusRequest,
)
from app.modules.procurement.integration.providers.inventory_receipt_status import (
    InventoryReceiptStatusQueryProvider,
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
    mutation, lifecycle rules, and duplicate receipt
    protection remain owned by the Inventory service boundary.
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

    def supports(self, operation: str) -> bool:
        """Return whether this provider supports the operation."""

        return operation in {
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
            INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION,
        }

    def validate(self, request: IntegrationRequest) -> None:
        """Validate the enterprise request and operation-specific payload."""

        super().validate(request)

        if not self.supports(request.operation):
            raise ValueError(
                "Unsupported Inventory integration operation."
            )

        if (
            request.operation
            == INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION
        ):
            if not isinstance(
                request.payload,
                PurchaseOrderLineReceiptStatusRequest,
            ):
                raise TypeError(
                    "Inventory receipt-status query payload must be a "
                    "PurchaseOrderLineReceiptStatusRequest."
                )
            return

        if not isinstance(
            request.payload,
            PurchaseOrderReceiptRequest,
        ):
            raise TypeError(
                "Inventory receipt integration payload must be a "
                "PurchaseOrderReceiptRequest."
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

        if (
            request.operation
            == INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION
        ):
            try:
                self.validate(request)
                result = InventoryReceiptStatusQueryProvider.query(
                    request.payload
                )
            except Exception:
                return IntegrationResponse(
                    success=False,
                    message=(
                        "Inventory receipt status could not be established."
                    ),
                    error="QUERY_FAILED",
                    request_id=request.request_id,
                )

            return IntegrationResponse(
                success=result.success,
                message=result.message or (
                    "Inventory receipt status queried successfully."
                    if result.success
                    else "Inventory receipt status is unavailable."
                ),
                data={
                    "success": result.success,
                    "purchase_order_reference": (
                        result.purchase_order_reference
                    ),
                    "purchase_order_line_reference": (
                        result.purchase_order_line_reference
                    ),
                    "received_quantity": result.received_quantity,
                    "unit": result.unit,
                    "receipt_count": result.receipt_count,
                    "has_receipts": result.has_receipts,
                    "error_code": result.error_code,
                },
                error=result.error_code,
                request_id=request.request_id,
            )

        try:
            self.validate(request)
        except (
            TypeError,
            ValueError,
            RuntimeError,
        ) as exc:
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
            .get_by_product_id(product.id)
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

        # Only complete, valid valuation evidence qualifies a receipt
        # as valued. Physical receipt remains possible without it.
        unit_price = receipt.valuation_unit_price
        currency = receipt.valuation_currency
        price_basis = receipt.valuation_price_basis

        has_valid_valuation = (
            isinstance(unit_price, Decimal)
            and unit_price.is_finite()
            and unit_price >= Decimal("0")
            and isinstance(currency, str)
            and currency in {"USD", "SSP"}
            and price_basis == "PO_LINE_UNIT_PRICE"
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
            valuation_status=(
                "VALUED" if has_valid_valuation else "UNVALUED"
            ),
            purchase_order_reference=(
                receipt.purchase_order_reference
            ),
            purchase_order_line_reference=(
                receipt.purchase_order_line_reference
            ),
            unit=receipt.unit,
            valuation_unit_price=(
                unit_price if has_valid_valuation else None
            ),
            valuation_currency=(
                currency if has_valid_valuation else None
            ),
            valuation_price_basis=(
                price_basis if has_valid_valuation else None
            ),
            occurred_at=receipt.received_at,
        )

        try:
            posted_movement = (
                self.movement_service
                .post_receipt_movement(
                    movement,
                    subject=request.metadata.get("subject", ""),
                    idempotency_key=receipt.idempotency_key,
                    purchase_order_reference=(
                        receipt.purchase_order_reference
                    ),
                    purchase_order_line_reference=(
                        receipt.purchase_order_line_reference
                    ),
                )
            )
        except Exception as exc:
            return IntegrationResponse(
                success=False,
                message=(
                    "Inventory receipt posting could not be completed."
                ),
                error=str(exc),
                request_id=request.request_id,
            )

        return IntegrationResponse(
            success=True,
            message="Inventory receipt posted successfully.",
            data={
                "stock_movement_id": posted_movement.id,
                "stock_item_id": posted_movement.stock_item_id,
                "location_id": posted_movement.location_id,
                "quantity": posted_movement.quantity,
                "movement_type": posted_movement.movement_type,
                "status": posted_movement.status,
                "receiving_reference": receipt.receiving_reference,
            },
            request_id=request.request_id,
        )


__all__ = [
    "InventoryReceiptIntegrationProvider",
]
