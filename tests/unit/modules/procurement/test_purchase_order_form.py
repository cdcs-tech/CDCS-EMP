"""
Tests for the Procurement Purchase Order form.
"""

from datetime import date

from app.modules.procurement.forms import PurchaseOrderForm


def _build_form(app, data):
    app.config["WTF_CSRF_ENABLED"] = False

    form = PurchaseOrderForm(data=data)
    form.supplier_id.choices = [
        (1, "Supplier 1"),
        (2, "Supplier 2"),
    ]
    form.purchase_request_id.choices = [
        (1, "PR-001"),
        (2, "PR-002"),
    ]

    return form


def test_purchase_order_form_accepts_valid_data(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "expected_delivery_date": date(2026, 9, 25),
                "status": "DRAFT",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is True


def test_purchase_order_form_requires_reference(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "",
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "status": "DRAFT",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is False
        assert form.reference.errors


def test_purchase_order_form_requires_supplier(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": None,
                "order_date": date(2026, 9, 18),
                "status": "DRAFT",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is False
        assert form.supplier_id.errors


def test_purchase_order_form_requires_order_date(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": 1,
                "order_date": None,
                "status": "DRAFT",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is False
        assert form.order_date.errors


def test_purchase_order_form_allows_blank_expected_delivery_date(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "expected_delivery_date": None,
                "status": "DRAFT",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is True


def test_purchase_order_form_requires_status(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "status": "",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is False
        assert form.status.errors


def test_purchase_order_form_requires_purchase_request(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "status": "DRAFT",
                "purchase_request_id": None,
            },
        )

        assert form.validate() is False
        assert form.purchase_request_id.errors


def test_purchase_order_form_rejects_overlength_reference(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "x" * 101,
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "status": "DRAFT",
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is False
        assert form.reference.errors


def test_purchase_order_form_rejects_overlength_status(app):
    with app.test_request_context():
        form = _build_form(
            app,
            {
                "reference": "PO-001",
                "supplier_id": 1,
                "order_date": date(2026, 9, 18),
                "status": "x" * 21,
                "purchase_request_id": 1,
            },
        )

        assert form.validate() is False
        assert form.status.errors
