from decimal import Decimal

from app.modules.catering.forms import StockTransferForm


STOCK_ITEM_CHOICES = [
    (1, "Stock Item One"),
    (2, "Stock Item Two"),
]

LOCATION_CHOICES = [
    (1, "Main Store"),
    (2, "Kitchen"),
]


def _form(data=None):
    """
    Build a StockTransferForm with realistic selector choices.
    """

    form = StockTransferForm(
        data=data,
    )

    form.stock_item_id.choices = STOCK_ITEM_CHOICES
    form.source_location_id.choices = LOCATION_CHOICES
    form.destination_location_id.choices = LOCATION_CHOICES

    return form


def test_stock_transfer_form_has_expected_fields(app):
    with app.test_request_context():
        form = StockTransferForm()

        assert set(form._fields) == {
            "stock_item_id",
            "source_location_id",
            "destination_location_id",
            "quantity",
            "reference",
            "reason",
            "occurred_at",
        }


def test_stock_transfer_form_accepts_valid_values(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.500"),
                "reference": "TRF-001",
                "reason": "Transfer to kitchen",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is True


def test_stock_transfer_form_requires_stock_item(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": None,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.stock_item_id.errors


def test_stock_transfer_form_requires_source_location(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": None,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.source_location_id.errors


def test_stock_transfer_form_requires_destination_location(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": None,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.destination_location_id.errors


def test_stock_transfer_form_requires_quantity(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": None,
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.quantity.errors


def test_stock_transfer_form_rejects_zero_quantity(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("0.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.quantity.errors


def test_stock_transfer_form_rejects_negative_quantity(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("-5.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.quantity.errors


def test_stock_transfer_form_requires_reference(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.reference.errors


def test_stock_transfer_form_rejects_reference_over_max_length(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "R" * 101,
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.reference.errors


def test_stock_transfer_form_requires_reason(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.reason.errors


def test_stock_transfer_form_rejects_reason_over_max_length(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "R" * 501,
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is False
        assert form.reason.errors


def test_stock_transfer_form_requires_occurred_at(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": None,
            }
        )

        assert form.validate() is False
        assert form.occurred_at.errors


def test_stock_transfer_form_parses_occurred_at(app):
    with app.test_request_context():
        form = _form(
            {
                "stock_item_id": 1,
                "source_location_id": 1,
                "destination_location_id": 2,
                "quantity": Decimal("10.000"),
                "reference": "TRF-001",
                "reason": "Transfer",
                "occurred_at": "2026-08-31T10:30",
            }
        )

        assert form.validate() is True
        assert form.occurred_at.data is not None


def test_stock_transfer_form_does_not_expose_lifecycle_fields(app):
    """
    Transfer lifecycle fields must remain outside the creation form.
    """

    with app.test_request_context():
        form = StockTransferForm()

        assert "status" not in form._fields
        assert "posted_at" not in form._fields
