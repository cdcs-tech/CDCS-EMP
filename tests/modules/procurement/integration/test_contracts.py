from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.modules.procurement.integration import (
    FINANCE_INTEGRATION_PROVIDER,
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    ProcurementFinancialEffectLine,
    ProcurementFinancialEffectRequest,
    PurchaseOrderReceiptRequest,
)


def build_receipt_request(**overrides):
    values = {
        "purchase_order_reference": "PO-001",
        "purchase_order_line_reference": "POL-001",
        "stock_item_reference": "STOCK-001",
        "inventory_location_reference": "MAIN",
        "quantity_received": Decimal("4.000"),
        "unit": "each",
        "received_at": datetime.now(timezone.utc),
        "receiving_reference": "GRN-001",
        "idempotency_key": "receipt:PO-001:POL-001:GRN-001",
        "notes": "Partial receipt",
    }
    values.update(overrides)
    return PurchaseOrderReceiptRequest(**values)


def build_financial_effect_line(**overrides):
    values = {
        "purchase_order_line_reference": "POL-001",
        "description": "Office chairs",
        "quantity": Decimal("10.000"),
        "unit": "each",
        "unit_price": Decimal("125.00"),
        "line_amount": Decimal("1250.00"),
    }
    values.update(overrides)
    return ProcurementFinancialEffectLine(**values)


def build_financial_effect_request(**overrides):
    values = {
        "purchase_order_reference": "PO-001",
        "purchase_request_reference": "PR-001",
        "supplier_reference": "SUP-001",
        "purchase_order_date": datetime(2026, 9, 25, 9, 0, tzinfo=timezone.utc),
        "approved_at": datetime(2026, 9, 25, 10, 0, tzinfo=timezone.utc),
        "currency": "USD",
        "total_procurement_value": Decimal("1250.00"),
        "purchase_order_lines": (build_financial_effect_line(),),
        "idempotency_key": "procurement-commitment:PO-001",
    }
    values.update(overrides)
    return ProcurementFinancialEffectRequest(**values)


# ---------------------------------------------------------------------------
# Inventory contract tests
# ---------------------------------------------------------------------------


def test_inventory_provider_identity():
    assert INVENTORY_INTEGRATION_PROVIDER == "inventory"


def test_inventory_receive_operation_identity():
    assert (
        INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        == "receive_purchase_order"
    )


def test_valid_receipt_contract_accepts_expected_fields():
    request = build_receipt_request()

    assert request.purchase_order_reference == "PO-001"
    assert request.quantity_received == Decimal("4.000")
    assert request.notes == "Partial receipt"


def test_receipt_contract_is_immutable():
    request = build_receipt_request()

    with pytest.raises(AttributeError):
        request.quantity_received = Decimal("5.000")


@pytest.mark.parametrize(
    "field",
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
def test_receipt_required_string_fields_reject_empty_values(field):
    with pytest.raises(ValueError):
        build_receipt_request(**{field: ""})


def test_receipt_quantity_must_be_positive():
    with pytest.raises(ValueError):
        build_receipt_request(quantity_received=Decimal("0"))


def test_receipt_quantity_rejects_negative_value():
    with pytest.raises(ValueError):
        build_receipt_request(quantity_received=Decimal("-1"))


def test_receipt_quantity_must_use_decimal():
    with pytest.raises(TypeError):
        build_receipt_request(quantity_received=4)


def test_receipt_received_at_must_be_datetime():
    with pytest.raises(TypeError):
        build_receipt_request(received_at="2026-09-25T10:00:00Z")


def test_receipt_notes_are_optional():
    request = build_receipt_request(notes=None)

    assert request.notes is None


def test_receipt_notes_must_be_string():
    with pytest.raises(TypeError):
        build_receipt_request(notes=123)


def test_receipt_contract_supports_partial_receipts():
    request = build_receipt_request(quantity_received=Decimal("2.000"))

    assert request.quantity_received == Decimal("2.000")


# ---------------------------------------------------------------------------
# Finance contract tests
# ---------------------------------------------------------------------------


def test_finance_provider_identity():
    assert FINANCE_INTEGRATION_PROVIDER == "finance"


def test_finance_procurement_commitment_operation_identity():
    assert (
        FINANCE_PROCUREMENT_COMMITMENT_OPERATION
        == "procurement_commitment"
    )


def test_valid_financial_effect_line_accepts_procurement_facts():
    line = build_financial_effect_line()

    assert line.purchase_order_line_reference == "POL-001"
    assert line.quantity == Decimal("10.000")
    assert line.unit_price == Decimal("125.00")
    assert line.line_amount == Decimal("1250.00")


def test_financial_effect_line_is_immutable():
    line = build_financial_effect_line()

    with pytest.raises(AttributeError):
        line.quantity = Decimal("5.000")


@pytest.mark.parametrize(
    "field",
    [
        "purchase_order_line_reference",
        "description",
        "unit",
    ],
)
def test_financial_effect_line_required_strings_reject_empty_values(field):
    with pytest.raises(ValueError):
        build_financial_effect_line(**{field: ""})


def test_financial_effect_line_quantity_must_use_decimal():
    with pytest.raises(TypeError):
        build_financial_effect_line(quantity=10)


def test_financial_effect_line_quantity_must_be_positive():
    with pytest.raises(ValueError):
        build_financial_effect_line(quantity=Decimal("0"))


def test_financial_effect_line_unit_price_must_use_decimal():
    with pytest.raises(TypeError):
        build_financial_effect_line(unit_price=125)


def test_financial_effect_line_unit_price_must_not_be_negative():
    with pytest.raises(ValueError):
        build_financial_effect_line(unit_price=Decimal("-1"))


def test_financial_effect_line_amount_must_use_decimal():
    with pytest.raises(TypeError):
        build_financial_effect_line(line_amount=1250)


def test_financial_effect_line_amount_must_not_be_negative():
    with pytest.raises(ValueError):
        build_financial_effect_line(line_amount=Decimal("-1"))


def test_valid_financial_effect_request_accepts_procurement_facts():
    request = build_financial_effect_request()

    assert request.purchase_order_reference == "PO-001"
    assert request.purchase_request_reference == "PR-001"
    assert request.supplier_reference == "SUP-001"
    assert request.currency == "USD"
    assert request.total_procurement_value == Decimal("1250.00")
    assert len(request.purchase_order_lines) == 1


def test_financial_effect_request_is_immutable():
    request = build_financial_effect_request()

    with pytest.raises(AttributeError):
        request.currency = "SSP"


@pytest.mark.parametrize(
    "field",
    [
        "purchase_order_reference",
        "purchase_request_reference",
        "supplier_reference",
        "currency",
        "idempotency_key",
    ],
)
def test_financial_effect_required_strings_reject_empty_values(field):
    with pytest.raises(ValueError):
        build_financial_effect_request(**{field: ""})


def test_financial_effect_purchase_order_date_must_be_datetime():
    with pytest.raises(TypeError):
        build_financial_effect_request(
            purchase_order_date="2026-09-25T09:00:00Z"
        )


def test_financial_effect_approved_at_must_be_datetime():
    with pytest.raises(TypeError):
        build_financial_effect_request(
            approved_at="2026-09-25T10:00:00Z"
        )


def test_financial_effect_total_value_must_use_decimal():
    with pytest.raises(TypeError):
        build_financial_effect_request(total_procurement_value=1250)


def test_financial_effect_total_value_must_not_be_negative():
    with pytest.raises(ValueError):
        build_financial_effect_request(
            total_procurement_value=Decimal("-1")
        )


def test_financial_effect_lines_must_be_tuple():
    with pytest.raises(TypeError):
        build_financial_effect_request(
            purchase_order_lines=[build_financial_effect_line()]
        )


def test_financial_effect_lines_must_not_be_empty():
    with pytest.raises(ValueError):
        build_financial_effect_request(purchase_order_lines=())


def test_financial_effect_lines_must_contain_contract_instances():
    with pytest.raises(TypeError):
        build_financial_effect_request(
            purchase_order_lines=("POL-001",)
        )


def test_financial_effect_idempotency_key_must_be_present():
    with pytest.raises(ValueError):
        build_financial_effect_request(idempotency_key="")


def test_financial_effect_contract_contains_no_accounting_semantics():
    request = build_financial_effect_request()

    assert not hasattr(request, "ledger_account")
    assert not hasattr(request, "journal_entry")
    assert not hasattr(request, "payment_reference")
    assert not hasattr(request, "invoice_reference")
    assert not hasattr(request, "debit")
    assert not hasattr(request, "credit")
