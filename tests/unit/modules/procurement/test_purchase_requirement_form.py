"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase requirement form tests.
"""

from datetime import date

from app.modules.procurement.forms import PurchaseRequirementForm


def test_purchase_requirement_form_accepts_valid_data(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "Office catering supplies",
                "source_module": "CATERING",
                "source_type": "Event",
                "source_reference": "CAT-EVT-001",
                "required_by_date": date(2026, 10, 15),
                "status": "DRAFT",
            },
        )

        assert form.validate() is True


def test_purchase_requirement_form_requires_reference(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "",
                "description": "Office catering supplies",
                "status": "DRAFT",
            },
        )

        assert form.validate() is False
        assert form.reference.errors


def test_purchase_requirement_form_requires_description(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "",
                "status": "DRAFT",
            },
        )

        assert form.validate() is False
        assert form.description.errors


def test_purchase_requirement_form_allows_optional_source_fields(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "Office catering supplies",
                "source_module": "",
                "source_type": "",
                "source_reference": "",
                "status": "DRAFT",
            },
        )

        assert form.validate() is True


def test_purchase_requirement_form_allows_optional_required_by_date(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "Office catering supplies",
                "required_by_date": "",
                "status": "DRAFT",
            },
        )

        assert form.validate() is True


def test_purchase_requirement_form_requires_status(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "Office catering supplies",
                "status": "",
            },
        )

        assert form.validate() is False
        assert form.status.errors


def test_purchase_requirement_form_rejects_overlength_reference(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "X" * 101,
                "description": "Office catering supplies",
                "status": "DRAFT",
            },
        )

        assert form.validate() is False
        assert form.reference.errors


def test_purchase_requirement_form_rejects_overlength_description(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "X" * 501,
                "status": "DRAFT",
            },
        )

        assert form.validate() is False
        assert form.description.errors


def test_purchase_requirement_form_accepts_status_without_workflow_transition_validation(app):
    with app.test_request_context():
        form = PurchaseRequirementForm(
            data={
                "reference": "PR-REQ-001",
                "description": "Office catering supplies",
                "status": "SUBMITTED",
            },
        )

        assert form.validate() is True
