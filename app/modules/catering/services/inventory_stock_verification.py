"""Inventory-owned verification of existing-stock evidence.

This implementation validates evidence supplied by an injected provider.
It does not query the database or infer approval from stock movements.

The evidence provider is an interim contract boundary. Its backing record
and approval workflow must be designed and approved separately.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from app.modules.catering.services.inventory_contracts import (
    InventoryStockVerificationResult,
)


class InventoryStockVerificationService:
    """Verify existing-stock eligibility using an injected evidence provider.

    The provider must expose ``get_approved_stock_evidence`` and return
    an approved evidence object or ``None``. The service fails closed
    for missing, malformed, unapproved, or mismatched evidence.
    """

    QUANTITY_SCALE = Decimal("0.001")
    APPROVED_STATUS = "APPROVED"
    ALLOWED_EVIDENCE_TYPES = frozenset(
        {
            "OPENING_STOCK",
            "INVENTORY_VERIFICATION",
        }
    )

    def __init__(self, *, evidence_provider: Any) -> None:
        if evidence_provider is None:
            raise ValueError("An existing-stock evidence provider is required.")
        self._evidence_provider = evidence_provider

    @classmethod
    def _positive_quantity(cls, value: object, field: str) -> Decimal:
        try:
            quantity = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be a valid decimal quantity.") from exc

        if not quantity.is_finite() or quantity <= 0:
            raise ValueError(f"{field} must be positive and finite.")

        if quantity != quantity.quantize(cls.QUANTITY_SCALE):
            raise ValueError(f"{field} cannot exceed three decimal places.")

        return quantity

    @staticmethod
    def _required_text(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} is required.")
        return value.strip()

    def verify_stock_eligibility(
        self,
        *,
        stock_item_id: int,
        location_id: int,
        quantity: Decimal,
        unit: str,
    ) -> InventoryStockVerificationResult:
        """Verify that approved evidence covers the requested quantity."""
        if isinstance(stock_item_id, bool) or not isinstance(stock_item_id, int) or stock_item_id <= 0:
            raise ValueError("stock_item_id must be a positive integer.")

        if isinstance(location_id, bool) or not isinstance(location_id, int) or location_id <= 0:
            raise ValueError("location_id must be a positive integer.")

        requested_quantity = self._positive_quantity(
            quantity,
            "Requested quantity",
        )
        requested_unit = self._required_text(unit, "Unit").casefold()

        evidence = self._evidence_provider.get_approved_stock_evidence(
            stock_item_id=stock_item_id,
            location_id=location_id,
        )

        if evidence is None:
            return InventoryStockVerificationResult(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=requested_unit,
                verified_quantity=Decimal("0.000"),
                verified=False,
                reason="No approved existing-stock evidence was found.",
            )

        status = getattr(evidence, "status", None)
        if not isinstance(status, str) or status.strip().upper() != self.APPROVED_STATUS:
            return InventoryStockVerificationResult(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=requested_unit,
                verified_quantity=Decimal("0.000"),
                verified=False,
                reason="Existing-stock evidence is not approved.",
            )

        evidence_type = getattr(evidence, "evidence_type", None)
        if (
            not isinstance(evidence_type, str)
            or evidence_type.strip().upper() not in self.ALLOWED_EVIDENCE_TYPES
        ):
            return InventoryStockVerificationResult(
                stock_item_id=stock_item_id,
                location_id=location_id,
                unit=requested_unit,
                verified_quantity=Decimal("0.000"),
                verified=False,
                reason="Existing-stock evidence type is not eligible.",
            )

        if getattr(evidence, "stock_item_id", None) != stock_item_id:
            return self._failed_result(
                stock_item_id,
                location_id,
                requested_unit,
                "Existing-stock evidence refers to a different Stock Item.",
            )

        if getattr(evidence, "location_id", None) != location_id:
            return self._failed_result(
                stock_item_id,
                location_id,
                requested_unit,
                "Existing-stock evidence refers to a different location.",
            )

        try:
            evidence_unit = self._required_text(
                getattr(evidence, "unit", None),
                "Evidence unit",
            ).casefold()
            verified_quantity = self._positive_quantity(
                getattr(evidence, "verified_quantity", None),
                "Evidence verified quantity",
            )
            evidence_reference = self._required_text(
                getattr(evidence, "reference", None),
                "Evidence reference",
            )
        except ValueError as exc:
            return self._failed_result(
                stock_item_id,
                location_id,
                requested_unit,
                f"Existing-stock evidence is invalid: {exc}",
            )

        if evidence_unit != requested_unit:
            return self._failed_result(
                stock_item_id,
                location_id,
                requested_unit,
                "Existing-stock evidence uses a different unit.",
            )

        if verified_quantity < requested_quantity:
            return self._failed_result(
                stock_item_id,
                location_id,
                requested_unit,
                "Approved existing-stock evidence does not cover the "
                "requested quantity.",
            )

        return InventoryStockVerificationResult(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=requested_unit,
            verified_quantity=verified_quantity,
            verified=True,
            evidence_type=evidence_type.strip().upper(),
            evidence_reference=evidence_reference,
        )

    @staticmethod
    def _failed_result(
        stock_item_id: int,
        location_id: int,
        unit: str,
        reason: str,
    ) -> InventoryStockVerificationResult:
        return InventoryStockVerificationResult(
            stock_item_id=stock_item_id,
            location_id=location_id,
            unit=unit,
            verified_quantity=Decimal("0.000"),
            verified=False,
            reason=reason,
        )


__all__ = ["InventoryStockVerificationService"]
