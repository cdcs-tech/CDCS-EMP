from datetime import date
from decimal import Decimal

from app.modules.procurement.forms import PurchaseOrderLineForm


def _build_form(app, data=None):
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_request_context(
        "/purchase-orders/1/lines/create",
        method="POST",
        data=data or {},
    ):
        return PurchaseOrderLineForm()


def test_purchase_order_line_form_accepts_valid_data(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "item_reference": "WATER-500ML",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "170.00",
            "notes": "For office use.",
        },
    )

    assert form.validate() is True


def test_purchase_order_line_form_requires_description(app):
    form = _build_form(
        app,
        {
            "description": "",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "170.00",
        },
    )

    assert form.validate() is False
    assert form.description.errors


def test_purchase_order_line_form_requires_quantity(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "170.00",
        },
    )

    assert form.validate() is False
    assert form.quantity.errors


def test_purchase_order_line_form_requires_unit(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "20.000",
            "unit": "",
            "unit_price": "8.50",
            "total_amount": "170.00",
        },
    )

    assert form.validate() is False
    assert form.unit.errors


def test_purchase_order_line_form_requires_unit_price(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "",
            "total_amount": "170.00",
        },
    )

    assert form.validate() is False
    assert form.unit_price.errors


def test_purchase_order_line_form_requires_total_amount(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "",
        },
    )

    assert form.validate() is False
    assert form.total_amount.errors


def test_purchase_order_line_form_allows_optional_item_reference(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "170.00",
        },
    )

    assert form.validate() is True


def test_purchase_order_line_form_allows_optional_notes(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "20.000",
            "unit": "Carton",
            "unit_price": "8.50",
            "total_amount": "170.00",
            "notes": "",
        },
    )

    assert form.validate() is True


def test_purchase_order_line_form_preserves_decimal_precision(app):
    form = _build_form(
        app,
        {
            "description": "Bottled Water",
            "quantity": "20.125",
            "unit": "Carton",
            "unit_price": "8.75",
            "total_amount": "175.00",
        },
    )

    assert form.validate() is True
    assert form.quantity.data == Decimal("20.125")
    assert form.unit_price.data == Decimal("8.75")
    assert form.total_amount.data == Decimal("175.00")
