from werkzeug.datastructures import MultiDict

from app.modules.catering.forms import InventoryLocationForm


def test_inventory_location_form_has_expected_fields(app):
    with app.test_request_context():
        form = InventoryLocationForm()

        assert set(form._fields) == {
            "code",
            "name",
            "description",
            "is_active",
        }


def test_inventory_location_form_accepts_valid_values(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "MAIN-STORE",
                    "name": "Main Store",
                    "description": "Primary catering inventory location.",
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is True
        assert form.code.data == "MAIN-STORE"
        assert form.name.data == "Main Store"
        assert form.description.data == (
            "Primary catering inventory location."
        )


def test_inventory_location_form_requires_code(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "",
                    "name": "Main Store",
                    "description": "",
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is False
        assert form.code.errors


def test_inventory_location_form_requires_name(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "MAIN-STORE",
                    "name": "",
                    "description": "",
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is False
        assert form.name.errors


def test_inventory_location_form_allows_optional_description(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "MAIN-STORE",
                    "name": "Main Store",
                    "description": "",
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is True
        assert form.description.data == ""


def test_inventory_location_form_rejects_code_over_max_length(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "A" * 51,
                    "name": "Main Store",
                    "description": "",
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is False
        assert form.code.errors


def test_inventory_location_form_rejects_name_over_max_length(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "MAIN-STORE",
                    "name": "A" * 151,
                    "description": "",
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is False
        assert form.name.errors


def test_inventory_location_form_rejects_description_over_max_length(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "MAIN-STORE",
                    "name": "Main Store",
                    "description": "A" * 501,
                    "is_active": "y",
                }
            )
        )

        assert form.validate() is False
        assert form.description.errors


def test_inventory_location_form_defaults_active(app):
    with app.test_request_context():
        form = InventoryLocationForm()

        assert form.is_active.default is True


def test_inventory_location_form_accepts_inactive_value(app):
    with app.test_request_context():
        form = InventoryLocationForm(
            formdata=MultiDict(
                {
                    "code": "SECONDARY",
                    "name": "Secondary Store",
                    "description": "",
                }
            )
        )

        assert form.validate() is True
        assert form.is_active.data is False
