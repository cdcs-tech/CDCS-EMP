"""
Tests for Procurement ↔ Inventory integration contracts.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)


def build_request(**overrides):
    values = {
        "purchase_order_reference": "PO-2026-001",
        "purchase_order_line_reference": "POL-2026-001-01",
        "stock_item_reference": "STOCK-001",
        "inventory_location_reference": "MAIN-STORE",
        "quantity_received": Decimal("10.500"),
        "unit": "kg",
        "received_at": datetime(
            2026,
            9,
            19,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        "receiving_reference": "GRN-2026-001",
        "idempotency_key": "GRN-2026-001:POL-2026-001-01",
        "notes": "Partial receipt.",
    }

    values.update(overrides)

    return PurchaseOrderReceiptRequest(**values)


def test_inventory_provider_identity_is_locked():
    assert INVENTORY_INTEGRATION_PROVIDER == "inventory"


def test_receive_purchase_order_operation_identity_is_locked():
    assert (
        INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        == "receive_purchase_order"
    )


def test_purchase_order_receipt_request_accepts_valid_contract():
    request = build_request()

    assert request.purchase_order_reference == "PO-2026-001"
    assert (
        request.purchase_order_line_reference
        == "POL-2026-001-01"
    )
    assert request.stock_item_reference == "STOCK-001"
    assert (
        request.inventory_location_reference
        == "MAIN-STORE"
    )
    assert request.quantity_received == Decimal("10.500")
    assert request.unit == "kg"
    assert request.receiving_reference == "GRN-2026-001"
    assert (
        request.idempotency_key
        == "GRN-2026-001:POL-2026-001-01"
    )
    assert request.notes == "Partial receipt."


def test_purchase_order_receipt_request_is_immutable():
    request = build_request()

    with pytest.raises(AttributeError):
        request.quantity_received = Decimal("20.000")


@pytest.mark.parametrize(
    "field_name",
    [
        "purchase_order_reference",
        "purchase_order_line_reference",
        "stock_item_reference",
        "inventory_location_reference",
        "unit",
        "receiving_reference",
        "idempotency_key",
    ],
)
def test_required_string_fields_reject_empty_values(
    field_name,
):
    with pytest.raises(ValueError):
        build_request(**{field_name: ""})


def test_quantity_received_must_be_positive():
    with pytest.raises(ValueError):
        build_request(
            quantity_received=Decimal("0")
        )


def test_negative_quantity_received_is_rejected():
    with pytest.raises(ValueError):
        build_request(
            quantity_received=Decimal("-1.000")
        )


def test_quantity_received_must_use_decimal():
    with pytest.raises(TypeError):
        build_request(quantity_received=10.5)


def test_received_at_must_be_datetime():
    with pytest.raises(TypeError):
        build_request(
            received_at="2026-09-19T10:30:00Z"
        )


def test_notes_are_optional():
    request = build_request(notes=None)

    assert request.notes is None


def test_notes_must_be_string_when_supplied():
    with pytest.raises(TypeError):
        build_request(notes=123)


def test_partial_receipt_is_supported_by_contract():
    request = build_request(
        quantity_received=Decimal("2.500")
    )

    assert request.quantity_received == Decimal("2.500")
