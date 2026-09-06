from decimal import Decimal

from werkzeug.datastructures import MultiDict

from app.modules.catering.forms import StockItemForm


PRODUCT_CHOICES = [
    (1, "Product One"),
    (2, "Product Two"),
]


def test_stock_item_form_has_expected_fields(app):
    with app.test_request_context():
        form = StockItemForm()

        assert set(form._fields) == {
            "product_id",
            "minimum_level",
            "reorder_level",
            "is_active",
        }


def test_stock_item_form_accepts_valid_values(app):
    with app.test_request_context():
        form = StockItemForm(
            formdata=MultiDict(
                {
                    "product_id": "1",
                    "minimum_level": "2.500",
                    "reorder_level": "5.000",
                    "is_active": "y",
                }
            )
        )
        form.product_id.choices = PRODUCT_CHOICES

        assert form.validate() is True
        assert form.minimum_level.data == Decimal("2.500")
        assert form.reorder_level.data == Decimal("5.000")


def test_stock_item_form_requires_product(app):
    with app.test_request_context():
        form = StockItemForm(
            formdata=MultiDict(
                {
                    "product_id": "",
                    "minimum_level": "2.000",
                    "reorder_level": "5.000",
                    "is_active": "y",
                }
            )
        )
        form.product_id.choices = PRODUCT_CHOICES

        assert form.validate() is False
        assert form.product_id.errors


def test_stock_item_form_allows_optional_thresholds(app):
    with app.test_request_context():
        form = StockItemForm(
            formdata=MultiDict(
                {
                    "product_id": "1",
                    "minimum_level": "",
                    "reorder_level": "",
                    "is_active": "y",
                }
            )
        )
        form.product_id.choices = PRODUCT_CHOICES

        assert form.validate() is True


def test_stock_item_form_rejects_negative_minimum_level(app):
    with app.test_request_context():
        form = StockItemForm(
            formdata=MultiDict(
                {
                    "product_id": "1",
                    "minimum_level": "-1.000",
                    "reorder_level": "5.000",
                    "is_active": "y",
                }
            )
        )
        form.product_id.choices = PRODUCT_CHOICES

        assert form.validate() is False
        assert form.minimum_level.errors


def test_stock_item_form_rejects_negative_reorder_level(app):
    with app.test_request_context():
        form = StockItemForm(
            formdata=MultiDict(
                {
                    "product_id": "1",
                    "minimum_level": "2.000",
                    "reorder_level": "-1.000",
                    "is_active": "y",
                }
            )
        )
        form.product_id.choices = PRODUCT_CHOICES

        assert form.validate() is False
        assert form.reorder_level.errors


def test_stock_item_form_defaults_active(app):
    with app.test_request_context():
        form = StockItemForm()

        assert form.is_active.default is True
