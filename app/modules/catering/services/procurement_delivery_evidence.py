"""Resolve approved Procurement lines and query their posted receipt evidence."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select

from app.core.crud.exceptions import EntityValidationException
from app.core.integration import IntegrationRequest, integration_service
from app.extensions import db
from app.modules.catering.models import (
    CateringPurchaseRequirement,
    Product,
    StockItem,
)
from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION,
    PurchaseOrderLineReceiptStatusRequest,
    InventoryReceiptStatusQueryResult,
)
from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequest,
    PurchaseRequirement,
)


class ProcurementDeliveryEvidenceResolver:
    """Resolve one unambiguous approved PO line and query its receipts."""

    def get_receipt_status(self, event_requirement: object) -> Any:
        requirement_id = getattr(event_requirement, "id", None)
        if requirement_id is None:
            self._reject("Procurement Event Requirement is not persisted.")

        catering_requirement = db.session.execute(
            select(CateringPurchaseRequirement).where(
                CateringPurchaseRequirement.event_requirement_id
                == requirement_id,
                CateringPurchaseRequirement.is_deleted == False,
            )
        ).scalar_one_or_none()

        if catering_requirement is None:
            self._reject(
                "Procurement fulfilment has no linked Catering Purchase Requirement."
            )

        procurement_reference = catering_requirement.procurement_reference
        if not procurement_reference:
            self._reject(
                "Catering Purchase Requirement has no Procurement reference."
            )

        procurement_requirement = db.session.execute(
            select(PurchaseRequirement).where(
                PurchaseRequirement.reference == procurement_reference,
                PurchaseRequirement.is_deleted == False,
            )
        ).scalar_one_or_none()

        if procurement_requirement is None:
            self._reject(
                "Linked Procurement Purchase Requirement could not be found."
            )

        purchase_requests = list(
            db.session.execute(
                select(PurchaseRequest).where(
                    PurchaseRequest.purchase_requirement_id
                    == procurement_requirement.id,
                    PurchaseRequest.is_deleted == False,
                )
            ).scalars().all()
        )

        approved_requests = [
            request
            for request in purchase_requests
            if request.status == "APPROVED"
        ]
        if not approved_requests:
            self._reject(
                "Procurement fulfilment requires an APPROVED Purchase Request."
            )

        item_reference = getattr(event_requirement, "item_reference", None)
        required_unit = self._normalize_unit(
            getattr(event_requirement, "unit", None)
        )
        stock_item_id = getattr(event_requirement, "stock_item_id", None)

        if not item_reference or not required_unit or stock_item_id is None:
            self._reject(
                "Procurement fulfilment requires an item reference, stock item, and unit."
            )

        stock_item = db.session.get(StockItem, stock_item_id)
        if (
            stock_item is None
            or getattr(stock_item, "is_deleted", False)
            or stock_item.product is None
            or getattr(stock_item.product, "is_deleted", False)
        ):
            self._reject(
                "Procurement fulfilment stock item or Product is unavailable."
            )

        stock_item_reference = stock_item.product.code
        if not stock_item_reference:
            self._reject(
                "Procurement fulfilment Product has no stock-item reference."
            )

        candidate_lines: list[tuple[PurchaseOrder, PurchaseOrderLine]] = []

        for purchase_request in approved_requests:
            request_lines = [
                line
                for line in purchase_request.lines
                if not getattr(line, "is_deleted", False)
                and line.item_reference == item_reference
                and self._normalize_unit(line.unit) == required_unit
            ]

            if not request_lines:
                continue

            if len(request_lines) != 1:
                self._reject(
                    "Procurement Purchase Request has ambiguous matching lines."
                )

            purchase_orders = list(
                db.session.execute(
                    select(PurchaseOrder).where(
                        PurchaseOrder.purchase_request_id == purchase_request.id,
                        PurchaseOrder.is_deleted == False,
                    )
                ).scalars().all()
            )

            for purchase_order in purchase_orders:
                if purchase_order.status != "APPROVED":
                    continue

                matching_order_lines = [
                    line
                    for line in purchase_order.lines
                    if not getattr(line, "is_deleted", False)
                    and line.item_reference == item_reference
                    and line.stock_item_reference == stock_item_reference
                    and self._normalize_unit(line.unit) == required_unit
                ]

                if len(matching_order_lines) > 1:
                    self._reject(
                        "Approved Purchase Order has ambiguous matching lines."
                    )

                if matching_order_lines:
                    candidate_lines.append(
                        (purchase_order, matching_order_lines[0])
                    )

        if len(candidate_lines) != 1:
            self._reject(
                "Procurement fulfilment requires exactly one consistent approved Purchase Order line."
            )

        purchase_order, purchase_order_line = candidate_lines[0]

        query = PurchaseOrderLineReceiptStatusRequest(
            purchase_order_reference=purchase_order.reference,
            purchase_order_line_reference=(
                f"PO-LINE-{purchase_order_line.guid}"
            ),
            stock_item_reference=stock_item_reference,
        )

        try:
            integration_result = integration_service.execute(
                IntegrationRequest(
                    provider=INVENTORY_INTEGRATION_PROVIDER,
                    operation=(
                        INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION
                    ),
                    payload=query,
                )
            )
        except Exception as exc:
            raise EntityValidationException(
                "Inventory receipt evidence query is unavailable."
            ) from exc

        if not integration_result.success:
            self._reject(
                "Inventory receipt evidence query is unavailable."
            )

        response = integration_result.response
        receipt_status_data = getattr(response, "data", None)

        if not isinstance(receipt_status_data, dict):
            self._reject(
                "Inventory receipt evidence query is unavailable."
            )

        if receipt_status_data.get("success") is not True:
            self._reject(
                "Inventory receipt evidence query is unavailable."
            )

        if (
            receipt_status_data.get("purchase_order_reference")
            != purchase_order.reference
            or receipt_status_data.get("purchase_order_line_reference")
            != query.purchase_order_line_reference
        ):
            self._reject(
                "Inventory receipt evidence does not match the approved Purchase Order line."
            )

        try:
            receipt_status = InventoryReceiptStatusQueryResult(
                success=receipt_status_data["success"],
                purchase_order_reference=receipt_status_data[
                    "purchase_order_reference"
                ],
                purchase_order_line_reference=receipt_status_data[
                    "purchase_order_line_reference"
                ],
                received_quantity=receipt_status_data["received_quantity"],
                unit=receipt_status_data["unit"],
                receipt_count=receipt_status_data["receipt_count"],
                has_receipts=receipt_status_data["has_receipts"],
                error_code=receipt_status_data.get("error_code"),
            )
        except (KeyError, TypeError, ValueError):
            self._reject(
                "Inventory receipt evidence query is unavailable."
            )

        return receipt_status

    @staticmethod
    def _normalize_unit(value: Any) -> str | None:
        if not isinstance(value, str) or not value.strip():
            return None
        return value.strip().casefold()

    @staticmethod
    def _reject(message: str) -> None:
        raise EntityValidationException(message)


__all__ = ["ProcurementDeliveryEvidenceResolver"]
