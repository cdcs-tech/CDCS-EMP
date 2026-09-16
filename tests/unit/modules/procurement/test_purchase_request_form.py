"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase request form tests.
"""

from datetime import date

from app.modules.procurement.forms import PurchaseRequestForm


def test_purchase_request_form_accepts_valid_data(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "required_by_date": date(2026, 10, 15),
                "status": "DRAFT",
                "justification": "Office catering supplies required.",
                "notes": "Required for the scheduled activity.",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
            (2, "PR-REQ-002"),
        ]

        assert form.validate() is True


def test_purchase_request_form_requires_reference(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "DRAFT",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.reference.errors


def test_purchase_request_form_requires_purchase_requirement(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 0,
                "request_date": date(2026, 10, 1),
                "status": "DRAFT",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.purchase_requirement_id.errors


def test_purchase_request_form_requires_request_date(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": "",
                "status": "DRAFT",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.request_date.errors


def test_purchase_request_form_allows_optional_required_by_date(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "required_by_date": "",
                "status": "DRAFT",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is True


def test_purchase_request_form_allows_optional_justification_and_notes(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "DRAFT",
                "justification": "",
                "notes": "",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is True


def test_purchase_request_form_requires_status(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.status.errors


def test_purchase_request_form_rejects_overlength_reference(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "X" * 101,
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "DRAFT",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.reference.errors


def test_purchase_request_form_rejects_overlength_justification(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "DRAFT",
                "justification": "X" * 501,
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.justification.errors


def test_purchase_request_form_rejects_overlength_notes(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "DRAFT",
                "notes": "X" * 1001,
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is False
        assert form.notes.errors


def test_purchase_request_form_accepts_status_without_workflow_transition_validation(app):
    with app.test_request_context():
        form = PurchaseRequestForm(
            data={
                "reference": "PR-001",
                "purchase_requirement_id": 1,
                "request_date": date(2026, 10, 1),
                "status": "SUBMITTED",
            },
        )

        form.purchase_requirement_id.choices = [
            (1, "PR-REQ-001"),
        ]

        assert form.validate() is True
