
from decimal import Decimal
from types import SimpleNamespace

from app.modules.procurement.integration.contracts import (
    InventoryReceiptStatusQueryResult,
    PurchaseOrderLineReceiptStatusRequest,
)
from app.modules.procurement.integration.providers.inventory_receipt_status import (
    InventoryReceiptStatusQueryProvider,
)


def make_request(
    *,
    purchase_order_reference="PO-001",
    purchase_order_line_reference="LINE-001",
    stock_item_reference="WATER-001",
):
    return PurchaseOrderLineReceiptStatusRequest(
        purchase_order_reference=purchase_order_reference,
        purchase_order_line_reference=purchase_order_line_reference,
        stock_item_reference=stock_item_reference,
    )


class FakeResult:
    def __init__(self, *, scalar=None, rows=None):
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def all(self):
        return self.rows


def install_fake_inventory(
    monkeypatch,
    *,
    product=None,
    stock_item=None,
    rows=None,
    fail_on_call=None,
):
    import app.modules.procurement.integration.providers.inventory_receipt_status as module

    calls = {"count": 0, "statements": []}

    def fake_execute(statement):
        calls["count"] += 1
        calls["statements"].append(statement)

        if calls["count"] == fail_on_call:
            raise RuntimeError("Simulated Inventory query failure")

        if calls["count"] == 1:
            return FakeResult(scalar=product)

        if calls["count"] == 2:
            return FakeResult(scalar=stock_item)

        return FakeResult(rows=rows)

    monkeypatch.setattr(module.db.session, "execute", fake_execute)
    monkeypatch.setattr(module.db.session, "rollback", lambda: None)
    return calls


def valid_product():
    return SimpleNamespace(id=10, code="WATER-001", unit="bottle")


def valid_stock_item():
    return SimpleNamespace(id=20, product_id=10)


def test_valid_mapping_without_receipts_returns_decimal_zero(monkeypatch):
    calls = install_fake_inventory(
        monkeypatch,
        product=valid_product(),
        stock_item=valid_stock_item(),
        rows=[],
    )

    result = InventoryReceiptStatusQueryProvider.query(make_request())

    assert isinstance(result, InventoryReceiptStatusQueryResult)
    assert result.success is True
    assert result.received_quantity == Decimal("0")
    assert result.unit == "bottle"
    assert result.receipt_count == 0
    assert result.has_receipts is False
    assert calls["count"] == 3


def test_multiple_distinct_receipts_are_aggregated_exactly(monkeypatch):
    rows = [
        SimpleNamespace(
            id=101,
            quantity=Decimal("2.125"),
            product_id=10,
        ),
        SimpleNamespace(
            id=102,
            quantity=Decimal("3.250"),
            product_id=10,
        ),
    ]
    install_fake_inventory(
        monkeypatch,
        product=valid_product(),
        stock_item=valid_stock_item(),
        rows=rows,
    )

    result = InventoryReceiptStatusQueryProvider.query(make_request())

    assert result.success is True
    assert result.received_quantity == Decimal("5.375")
    assert result.unit == "bottle"
    assert result.receipt_count == 2
    assert result.has_receipts is True


def test_receipt_for_another_product_is_unavailable(monkeypatch):
    rows = [
        SimpleNamespace(
            id=101,
            quantity=Decimal("2.000"),
            product_id=99,
        ),
    ]
    install_fake_inventory(
        monkeypatch,
        product=valid_product(),
        stock_item=valid_stock_item(),
        rows=rows,
    )

    result = InventoryReceiptStatusQueryProvider.query(make_request())

    assert result.success is False
    assert result.error_code == "INCONSISTENT_RECEIPT_HISTORY"
    assert result.received_quantity is None
    assert result.has_receipts is None


def test_missing_product_mapping_is_not_reported_as_zero(monkeypatch):
    calls = install_fake_inventory(
        monkeypatch,
        product=None,
    )

    result = InventoryReceiptStatusQueryProvider.query(make_request())

    assert result.success is False
    assert result.error_code == "PRODUCT_MAPPING_NOT_FOUND"
    assert result.received_quantity is None
    assert result.receipt_count is None
    assert result.has_receipts is None
    assert calls["count"] == 1


def test_query_failure_is_distinct_from_zero_receipts(monkeypatch):
    install_fake_inventory(
        monkeypatch,
        fail_on_call=1,
    )

    result = InventoryReceiptStatusQueryProvider.query(make_request())

    assert result.success is False
    assert result.error_code == "QUERY_FAILED"
    assert result.received_quantity is None
    assert result.receipt_count is None
    assert result.has_receipts is None


def test_blank_references_are_rejected_before_database_access(monkeypatch):
    import app.modules.procurement.integration.providers.inventory_receipt_status as module

    def unexpected_execute(statement):
        raise AssertionError("Database access should not occur")

    monkeypatch.setattr(module.db.session, "execute", unexpected_execute)

    result = InventoryReceiptStatusQueryProvider.query(
        make_request(purchase_order_line_reference="   ")
    )

    assert result.success is False
    assert result.error_code == "INVALID_REFERENCES"
    assert result.received_quantity is None


def test_receipt_query_filters_exact_order_line_and_posted_receipts(
    monkeypatch,
):
    calls = install_fake_inventory(
        monkeypatch,
        product=valid_product(),
        stock_item=valid_stock_item(),
        rows=[],
    )

    result = InventoryReceiptStatusQueryProvider.query(make_request())

    assert result.success is True
    assert len(calls["statements"]) == 3

    statement = calls["statements"][2]
    compiled = statement.compile()
    sql = str(compiled).lower()
    parameters = set(compiled.params.values())

    assert "purchase_order_reference" in sql
    assert "purchase_order_line_reference" in sql
    assert "movement_type" in sql
    assert "status" in sql
    assert "posted_at" in sql
    assert "is not null" in sql

    assert "PO-001" in parameters
    assert "LINE-001" in parameters
    assert "RECEIPT" in parameters
    assert "POSTED" in parameters
