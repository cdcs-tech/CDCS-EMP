from datetime import date

from app.modules.procurement.forms import PurchaseRequestLineForm


def test_purchase_request_line_form_accepts_valid_data(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "item_reference": "STAT-001",
                "quantity": "10.000",
                "unit": "pack",
                "estimated_unit_cost": "25.50",
                "estimated_total": "255.00",
                "required_by_date": date(2026, 10, 15),
                "notes": "Required for office operations.",
            }
        )

        assert form.validate() is True


def test_purchase_request_line_form_requires_description(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "",
                "quantity": "10.000",
                "unit": "pack",
            }
        )

        assert form.validate() is False
        assert "description" in form.errors


def test_purchase_request_line_form_requires_quantity(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "quantity": "",
                "unit": "pack",
            }
        )

        assert form.validate() is False
        assert "quantity" in form.errors


def test_purchase_request_line_form_requires_unit(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "quantity": "10.000",
                "unit": "",
            }
        )

        assert form.validate() is False
        assert "unit" in form.errors


def test_purchase_request_line_form_accepts_optional_fields_as_blank(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "quantity": "10.000",
                "unit": "pack",
                "item_reference": "",
                "estimated_unit_cost": "",
                "estimated_total": "",
                "required_by_date": "",
                "notes": "",
            }
        )

        assert form.validate() is True


def test_purchase_request_line_form_rejects_overlength_description(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "A" * 501,
                "quantity": "10.000",
                "unit": "pack",
            }
        )

        assert form.validate() is False
        assert "description" in form.errors


def test_purchase_request_line_form_rejects_overlength_item_reference(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "item_reference": "A" * 101,
                "quantity": "10.000",
                "unit": "pack",
            }
        )

        assert form.validate() is False
        assert "item_reference" in form.errors


def test_purchase_request_line_form_rejects_overlength_unit(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "quantity": "10.000",
                "unit": "A" * 51,
            }
        )

        assert form.validate() is False
        assert "unit" in form.errors


def test_purchase_request_line_form_rejects_overlength_notes(app):
    with app.test_request_context():
        form = PurchaseRequestLineForm(
            data={
                "description": "Office stationery",
                "quantity": "10.000",
                "unit": "pack",
                "notes": "A" * 1001,
            }
        )

        assert form.validate() is False
        assert "notes" in form.errors
