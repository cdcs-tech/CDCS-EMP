"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Supplier form tests.
"""

from app.modules.procurement.forms import SupplierForm


def test_supplier_form_exposes_approved_fields(app):
    """
    Verify that SupplierForm exposes exactly the approved
    Supplier operational fields.
    """

    with app.test_request_context():
        form = SupplierForm()

        assert set(form._fields) == {
            "name",
            "code",
            "supplier_type",
            "contact_information",
            "address_information",
            "status",
        }


def test_supplier_form_field_lengths(app):
    """
    Verify that SupplierForm field lengths match the
    approved Supplier model constraints.
    """

    with app.test_request_context():
        form = SupplierForm()

        assert form.name.validators[1].max == 150
        assert form.code.validators[1].max == 50
        assert form.supplier_type.validators[1].max == 50
        assert form.contact_information.validators[0].max == 500
        assert form.address_information.validators[0].max == 500
        assert form.status.validators[1].max == 20


def test_supplier_form_requires_required_fields(app):
    """
    Verify that the approved required Supplier fields
    are enforced by the form.
    """

    with app.test_request_context():
        form = SupplierForm()

        assert not form.validate()
        assert form.name.errors
        assert form.code.errors
        assert form.supplier_type.errors
        assert form.status.errors


def test_supplier_form_accepts_valid_supplier_data(app):
    """
    Verify that valid Supplier data passes form validation.
    """

    with app.test_request_context():
        form = SupplierForm(
            data={
                "name": "Example Supplier Ltd",
                "code": "SUP-001",
                "supplier_type": "GENERAL",
                "contact_information": "info@example.com",
                "address_information": "Juba, South Sudan",
                "status": "ACTIVE",
            }
        )

        assert form.validate()


def test_supplier_form_has_no_financial_fields(app):
    """
    Verify that the Supplier operational form does not
    introduce deferred financial or settlement fields.
    """

    with app.test_request_context():
        form = SupplierForm()

        forbidden_fields = {
            "bank_account",
            "bank_name",
            "tax_number",
            "invoice",
            "payment",
            "settlement",
        }

        assert forbidden_fields.isdisjoint(form._fields)
