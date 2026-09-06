from datetime import datetime

from decimal import Decimal

from app.modules.catering.forms import StockMovementForm


STOCK_ITEM_CHOICES = [
    (1, "Stock Item One"),
    (2, "Stock Item Two"),
]

LOCATION_CHOICES = [
    (1, "Main Store"),
    (2, "Kitchen"),
]

VALID_MOVEMENT_TYPES = [
    "OPENING_BALANCE",
    "RECEIPT",
    "ISSUE",
    "ADJUSTMENT",
    "TRANSFER",
]


def _form(data=None):
    """
    Build a StockMovementForm with realistic selector choices.
    """

    form = StockMovementForm(
        data=data,
    )

    form.stock_item_id.choices = STOCK_ITEM_CHOICES
    form.location_id.choices = LOCATION_CHOICES

    return form


def test_stock_movement_form_has_expected_fields(app):
    with app.test_request_context():
        form = StockMovementForm()

        assert set(form._fields) == {
            "stock_item_id",
            "location_id",
            "movement_type",
            "quantity",
            "reference",
            "reason",
            "occurred_at",
        }


def test_stock_movement_form_accepts_valid_values(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": Decimal("10.500"),
                "reference": "GRN-001",
                "reason": "Initial stock receipt",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is True


def test_stock_movement_form_requires_stock_item(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": None,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.stock_item_id.errors


def test_stock_movement_form_requires_location(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": None,
                "movement_type": "RECEIPT",
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.location_id.errors


def test_stock_movement_form_requires_movement_type(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "",
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.movement_type.errors


def test_stock_movement_form_accepts_all_authoritative_movement_types(
    app,
):
    with app.test_request_context():
        for movement_type in VALID_MOVEMENT_TYPES:
            form = _form(
                {
                    "stock_item_id": 1,
                    "location_id": 1,
                    "movement_type": movement_type,
                    "quantity": Decimal("10.000"),
                    "reference": "",
                    "reason": "",
                    "occurred_at": "2026-08-31T10:30",
                }
            )

            assert form.validate() is True


def test_stock_movement_form_rejects_invalid_movement_type(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "INVALID",
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.movement_type.errors


def test_stock_movement_form_requires_quantity(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": None,
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.quantity.errors


def test_stock_movement_form_rejects_zero_quantity(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": Decimal("0.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.quantity.errors


def test_stock_movement_form_allows_negative_quantity(app):
    """
    Negative quantities are allowed at the form layer.

    The service layer determines whether the movement can actually
    be posted against the current stock balance.
    """

    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "ISSUE",
                "quantity": Decimal("-5.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is True


def test_stock_movement_form_allows_optional_reference_and_reason(
    app,
):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "ADJUSTMENT",
                "quantity": Decimal("2.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is True


def test_stock_movement_form_rejects_reference_over_max_length(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": Decimal("10.000"),
                "reference": "R" * 101,
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.reference.errors


def test_stock_movement_form_rejects_reason_over_max_length(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "ADJUSTMENT",
                "quantity": Decimal("2.000"),
                "reference": "",
                "reason": "R" * 501,
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.reason.errors


def test_stock_movement_form_requires_occurred_at(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "",
                "occurred_at": None,
            }
        )

        assert form.validate() is False
        assert form.occurred_at.errors


def test_stock_movement_form_parses_occurred_at(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "location_id": 1,
                "movement_type": "RECEIPT",
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is True
        assert form.occurred_at.data is not None

def test_stock_movement_form_does_not_expose_posting_fields(app):
    """
    Posting lifecycle fields must remain outside the creation form.
    """

    with app.test_request_context():
        form = StockMovementForm()

        assert "status" not in form._fields
        assert "posted_at" not in form._fields
        assert "transfer_id" not in form._fields
