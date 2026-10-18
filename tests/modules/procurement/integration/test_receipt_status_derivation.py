from decimal import Decimal

import pytest

from app.modules.procurement.integration.contracts import (
    InventoryReceiptStatusQueryResult,
)
from app.modules.procurement.integration.receipt_status import (
    FULLY_RECEIVED,
    NOT_RECEIVED,
    OVER_RECEIVED,
    PARTIALLY_RECEIVED,
    STATUS_UNAVAILABLE,
    derive_purchase_order_line_receipt_status,
)


def inventory_result(
    *,
    success=True,
    purchase_order_reference="PO-001",
    purchase_order_line_reference="LINE-001",
    received_quantity=Decimal("0"),
    unit="bottle",
    receipt_count=0,
    has_receipts=False,
    error_code=None,
):
    return InventoryReceiptStatusQueryResult(
        success=success,
        purchase_order_reference=purchase_order_reference,
        purchase_order_line_reference=purchase_order_line_reference,
        received_quantity=received_quantity,
        unit=unit,
        receipt_count=receipt_count,
        has_receipts=has_receipts,
        error_code=error_code,
    )


def derive(result, *, ordered_quantity=Decimal("12"), ordered_unit="bottle"):
    return derive_purchase_order_line_receipt_status(
        purchase_order_reference="PO-001",
        purchase_order_line_reference="LINE-001",
        ordered_quantity=ordered_quantity,
        ordered_unit=ordered_unit,
        inventory_result=result,
    )


@pytest.mark.parametrize(
    ("received", "count", "has_receipts", "expected_status"),
    [
        (Decimal("0"), 0, False, NOT_RECEIVED),
        (Decimal("5"), 1, True, PARTIALLY_RECEIVED),
        (Decimal("12"), 1, True, FULLY_RECEIVED),
        (Decimal("12.001"), 2, True, OVER_RECEIVED),
    ],
)
def test_derives_status_from_valid_receipt_facts(
    received,
    count,
    has_receipts,
    expected_status,
):
    result = inventory_result(
        received_quantity=received,
        receipt_count=count,
        has_receipts=has_receipts,
    )

    derived = derive(result)

    assert derived.status == expected_status
    assert derived.received_quantity == received
    assert derived.receipt_count == count
    assert derived.error_code is None


def test_decimal_comparison_does_not_use_float_tolerance():
    result = inventory_result(
        received_quantity=Decimal("11.999"),
        receipt_count=1,
        has_receipts=True,
    )

    derived = derive(result)

    assert derived.status == PARTIALLY_RECEIVED


def test_incompatible_units_are_unavailable():
    result = inventory_result(
        received_quantity=Decimal("5"),
        unit="case",
        receipt_count=1,
        has_receipts=True,
    )

    derived = derive(result)

    assert derived.status == STATUS_UNAVAILABLE
    assert derived.error_code == "INCOMPATIBLE_UNITS"
    assert derived.received_quantity is None


def test_unit_matching_only_trims_surrounding_whitespace():
    result = inventory_result(
        received_quantity=Decimal("5"),
        unit=" bottle ",
        receipt_count=1,
        has_receipts=True,
    )

    derived = derive(result)

    assert derived.status == PARTIALLY_RECEIVED
    assert derived.unit == "bottle"


def test_failed_inventory_query_is_unavailable():
    result = inventory_result(
        success=False,
        error_code="QUERY_FAILED",
    )

    derived = derive(result)

    assert derived.status == STATUS_UNAVAILABLE
    assert derived.error_code == "QUERY_FAILED"


def test_mismatched_purchase_order_line_reference_is_unavailable():
    result = inventory_result(
        purchase_order_line_reference="OTHER-LINE",
    )

    derived = derive(result)

    assert derived.status == STATUS_UNAVAILABLE
    assert derived.error_code == "RECEIPT_REFERENCE_MISMATCH"


@pytest.mark.parametrize(
    ("received", "count", "has_receipts"),
    [
        (Decimal("0"), 1, True),
        (Decimal("5"), 0, False),
        (Decimal("-1"), 1, True),
    ],
)
def test_inconsistent_receipt_history_is_unavailable(
    received,
    count,
    has_receipts,
):
    result = inventory_result(
        received_quantity=received,
        receipt_count=count,
        has_receipts=has_receipts,
    )

    derived = derive(result)

    assert derived.status == STATUS_UNAVAILABLE


@pytest.mark.parametrize(
    "ordered_quantity",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        12.0,
    ],
)
def test_invalid_ordered_quantity_is_unavailable(ordered_quantity):
    result = inventory_result()

    derived = derive(result, ordered_quantity=ordered_quantity)

    assert derived.status == STATUS_UNAVAILABLE
    assert derived.error_code == "INVALID_ORDERED_QUANTITY"
