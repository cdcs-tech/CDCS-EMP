from decimal import Decimal

from werkzeug.datastructures import MultiDict

from app.modules.catering.forms import EventRequirementForm


FULFILMENT_CHOICES = [
    ("INVENTORY", "Inventory"),
    ("PROCUREMENT", "Procurement"),
]


def test_event_requirement_form_has_expected_fields(app):
    with app.test_request_context():
        form = EventRequirementForm()

        assert set(form._fields) == {
            "description",
            "item_reference",
            "quantity",
            "unit",
            "fulfilment_type",
            "required_by_date",
            "notes",
        }


def test_event_requirement_form_accepts_valid_inventory_requirement(app):
    with app.test_request_context():
        form = EventRequirementForm(
            formdata=MultiDict(
                {
                    "description": "Drinking water",
                    "item_reference": "WATER-500ML",
                    "quantity": "120.000",
                    "unit": "bottles",
                    "fulfilment_type": "INVENTORY",
                    "required_by_date": "2026-10-15",
                    "notes": "For event guests.",
                }
            )
        )
        form.fulfilment_type.choices = FULFILMENT_CHOICES

        assert form.validate() is True
        assert form.quantity.data == Decimal("120.000")


def test_event_requirement_form_accepts_valid_procurement_requirement(app):
    with app.test_request_context():
        form = EventRequirementForm(
            formdata=MultiDict(
                {
                    "description": "Additional catering chairs",
                    "item_reference": "",
                    "quantity": "50.000",
                    "unit": "chairs",
                    "fulfilment_type": "PROCUREMENT",
                    "required_by_date": "2026-10-15",
                    "notes": "",
                }
            )
        )
        form.fulfilment_type.choices = FULFILMENT_CHOICES

        assert form.validate() is True


def test_event_requirement_form_requires_description(app):
    with app.test_request_context():
        form = EventRequirementForm(
            formdata=MultiDict(
                {
                    "description": "",
                    "item_reference": "",
                    "quantity": "10.000",
                    "unit": "units",
                    "fulfilment_type": "INVENTORY",
                }
            )
        )
        form.fulfilment_type.choices = FULFILMENT_CHOICES

        assert form.validate() is False
        assert form.description.errors


def test_event_requirement_form_requires_positive_quantity(app):
    with app.test_request_context():
        form = EventRequirementForm(
            formdata=MultiDict(
                {
                    "description": "Test item",
                    "item_reference": "",
                    "quantity": "0",
                    "unit": "units",
                    "fulfilment_type": "INVENTORY",
                }
            )
        )
        form.fulfilment_type.choices = FULFILMENT_CHOICES

        assert form.validate() is False
        assert form.quantity.errors


def test_event_requirement_form_requires_unit(app):
    with app.test_request_context():
        form = EventRequirementForm(
            formdata=MultiDict(
                {
                    "description": "Test item",
                    "item_reference": "",
                    "quantity": "5.000",
                    "unit": "",
                    "fulfilment_type": "INVENTORY",
                }
            )
        )
        form.fulfilment_type.choices = FULFILMENT_CHOICES

        assert form.validate() is False
        assert form.unit.errors


def test_event_requirement_form_requires_fulfilment_type(app):
    with app.test_request_context():
        form = EventRequirementForm(
            formdata=MultiDict(
                {
                    "description": "Test item",
                    "item_reference": "",
                    "quantity": "5.000",
                    "unit": "units",
                    "fulfilment_type": "",
                }
            )
        )
        form.fulfilment_type.choices = FULFILMENT_CHOICES

        assert form.validate() is False
        assert form.fulfilment_type.errors
