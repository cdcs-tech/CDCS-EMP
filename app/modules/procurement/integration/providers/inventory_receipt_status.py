
"""Read-only Inventory receipt-status queries for Procurement."""

from decimal import Decimal

from sqlalchemy import select

from app.extensions import db
from app.modules.catering.models.inventory_receipt_idempotency import (
    InventoryReceiptIdempotency,
)
from app.modules.catering.models.product import Product
from app.modules.catering.models.stock_item import StockItem
from app.modules.catering.models.stock_movement import StockMovement
from app.modules.procurement.integration.contracts import (
    InventoryReceiptStatusQueryResult,
    PurchaseOrderLineReceiptStatusRequest,
)


class InventoryReceiptStatusQueryProvider:
    """Return verified receipt facts for an individual Purchase Order Line."""

    @staticmethod
    def _unavailable(
        request: PurchaseOrderLineReceiptStatusRequest,
        error_code: str,
        message: str,
    ) -> InventoryReceiptStatusQueryResult:
        return InventoryReceiptStatusQueryResult(
            success=False,
            purchase_order_reference=request.purchase_order_reference,
            purchase_order_line_reference=request.purchase_order_line_reference,
            received_quantity=None,
            unit=None,
            receipt_count=None,
            has_receipts=None,
            error_code=error_code,
            message=message,
        )

    @classmethod
    def query(
        cls,
        request: PurchaseOrderLineReceiptStatusRequest,
    ) -> InventoryReceiptStatusQueryResult:
        """Aggregate qualifying posted receipts without modifying Inventory."""
        po_reference = request.purchase_order_reference
        line_reference = request.purchase_order_line_reference
        product_reference = request.stock_item_reference

        if any(
            not isinstance(value, str)
            or not value.strip()
            or len(value) > 100
            for value in (po_reference, line_reference, product_reference)
        ):
            return cls._unavailable(
                request,
                "INVALID_REFERENCES",
                "Purchase Order, line, and Inventory Product references must "
                "be nonblank strings of at most 100 characters.",
            )

        try:
            # Resolve the explicit Product-code mapping before querying receipts.
            product = db.session.execute(
                select(Product).where(Product.code == product_reference)
            ).scalar_one_or_none()

            if product is None:
                return cls._unavailable(
                    request,
                    "PRODUCT_MAPPING_NOT_FOUND",
                    "The Inventory Product mapping could not be established.",
                )

            stock_item = db.session.execute(
                select(StockItem).where(StockItem.product_id == product.id)
            ).scalar_one_or_none()

            if stock_item is None:
                return cls._unavailable(
                    request,
                    "STOCK_ITEM_MAPPING_NOT_FOUND",
                    "The mapped Inventory Product has no Stock Item.",
                )

            if not isinstance(product.unit, str) or not product.unit.strip():
                return cls._unavailable(
                    request,
                    "PRODUCT_UNIT_UNAVAILABLE",
                    "The mapped Inventory Product has no valid unit.",
                )

            unit = product.unit.strip()

            rows = db.session.execute(
                select(
                    InventoryReceiptIdempotency.id,
                    StockMovement.quantity,
                    StockItem.product_id.label("product_id"),
                )
                .select_from(InventoryReceiptIdempotency)
                .join(
                    StockMovement,
                    StockMovement.id
                    == InventoryReceiptIdempotency.stock_movement_id,
                )
                .join(
                    StockItem,
                    StockItem.id == StockMovement.stock_item_id,
                )
                .where(
                    InventoryReceiptIdempotency.purchase_order_reference
                    == po_reference,
                    InventoryReceiptIdempotency.purchase_order_line_reference
                    == line_reference,
                    StockMovement.movement_type == "RECEIPT",
                    StockMovement.status == "POSTED",
                    StockMovement.posted_at.is_not(None),
                )
                .order_by(InventoryReceiptIdempotency.id.asc())
            ).all()

            if not rows:
                return InventoryReceiptStatusQueryResult(
                    success=True,
                    purchase_order_reference=po_reference,
                    purchase_order_line_reference=line_reference,
                    received_quantity=Decimal("0"),
                    unit=unit,
                    receipt_count=0,
                    has_receipts=False,
                )

            if any(row.product_id != product.id for row in rows):
                return cls._unavailable(
                    request,
                    "INCONSISTENT_RECEIPT_HISTORY",
                    "The Purchase Order Line receipt history references an "
                    "Inventory Product other than the explicitly mapped Product.",
                )

            if any(
                not isinstance(row.quantity, Decimal)
                or row.quantity <= 0
                for row in rows
            ):
                return cls._unavailable(
                    request,
                    "INVALID_RECEIPT_QUANTITY",
                    "Receipt history contains an invalid quantity.",
                )

            quantity = sum(
                (row.quantity for row in rows),
                start=Decimal("0"),
            )

            return InventoryReceiptStatusQueryResult(
                success=True,
                purchase_order_reference=po_reference,
                purchase_order_line_reference=line_reference,
                received_quantity=quantity,
                unit=unit,
                receipt_count=len({row.id for row in rows}),
                has_receipts=True,
            )

        except Exception:
            db.session.rollback()
            return cls._unavailable(
                request,
                "QUERY_FAILED",
                "Inventory receipt status could not be established.",
            )


__all__ = ["InventoryReceiptStatusQueryProvider"]
