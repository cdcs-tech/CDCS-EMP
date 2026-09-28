"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Focused tests for the CateringRequest model.
"""

from datetime import date, datetime

from app.modules.catering.models import (
    CateringRequest,
    Customer,
)


def test_catering_request_has_expected_table_and_columns():
    assert CateringRequest.__tablename__ == "catering_requests"

    assert CateringRequest.id is not None
    assert CateringRequest.guid is not None

    assert CateringRequest.customer_id.property.columns[0].nullable is False
    assert CateringRequest.request_date.property.columns[0].nullable is False
    assert CateringRequest.requested_service.property.columns[0].nullable is False
    assert CateringRequest.service_date.property.columns[0].nullable is False
    assert CateringRequest.attendance.property.columns[0].nullable is False
    assert CateringRequest.requirements.property.columns[0].nullable is True
    assert CateringRequest.notes.property.columns[0].nullable is True
    assert CateringRequest.status.property.columns[0].nullable is False


def test_catering_request_has_expected_field_lengths():
    assert CateringRequest.requested_service.property.columns[0].type.length == 150
    assert CateringRequest.requirements.property.columns[0].type.length == 1000
    assert CateringRequest.notes.property.columns[0].type.length == 1000
    assert CateringRequest.status.property.columns[0].type.length == 20


def test_catering_request_has_expected_date_types():
    assert CateringRequest.request_date.property.columns[0].type.python_type is date
    assert CateringRequest.service_date.property.columns[0].type.python_type is date


def test_catering_request_has_expected_controlled_value_constraints():
    constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in CateringRequest.__table__.constraints
        if constraint.name
        in {
            "ck_catering_requests_attendance_positive",
            "ck_catering_requests_status",
        }
    }

    assert "ck_catering_requests_attendance_positive" in constraints
    assert "attendance > 0" in constraints[
        "ck_catering_requests_attendance_positive"
    ]

    assert "ck_catering_requests_status" in constraints
    assert "DRAFT" in constraints["ck_catering_requests_status"]
    assert "SUBMITTED" in constraints["ck_catering_requests_status"]
    assert "CANCELLED" in constraints["ck_catering_requests_status"]


def test_catering_request_inherits_enterprise_mixins():
    catering_request = CateringRequest(
        customer_id=1,
        request_date=date(2026, 9, 28),
        requested_service="Corporate Lunch",
        service_date=date(2026, 10, 15),
        attendance=50,
    )

    assert hasattr(catering_request, "created_at")
    assert hasattr(catering_request, "updated_at")
    assert hasattr(catering_request, "created_by")
    assert hasattr(catering_request, "updated_by")

    assert CateringRequest.is_deleted.property.columns[0].default.arg is False


def test_catering_request_has_expected_default_status():
    status_column = CateringRequest.status.property.columns[0]

    assert status_column.default.arg == "DRAFT"


def test_catering_request_accepts_expected_values():
    catering_request = CateringRequest(
        customer_id=1,
        request_date=date(2026, 9, 28),
        requested_service="Corporate Lunch",
        service_date=date(2026, 10, 15),
        attendance=50,
        requirements="Lunch service with vegetarian options.",
        notes="Customer requested delivery by 12:30.",
        status="SUBMITTED",
    )

    assert catering_request.customer_id == 1
    assert catering_request.request_date == date(2026, 9, 28)
    assert catering_request.requested_service == "Corporate Lunch"
    assert catering_request.service_date == date(2026, 10, 15)
    assert catering_request.attendance == 50
    assert catering_request.requirements == (
        "Lunch service with vegetarian options."
    )
    assert catering_request.notes == (
        "Customer requested delivery by 12:30."
    )
    assert catering_request.status == "SUBMITTED"


def test_catering_request_customer_relationship_is_bidirectional():
    customer = Customer(
        name="Example Customer",
        customer_type="INDIVIDUAL",
    )

    catering_request = CateringRequest(
        customer=customer,
        request_date=date(2026, 9, 28),
        requested_service="Private Catering",
        service_date=date(2026, 10, 20),
        attendance=25,
    )

    assert catering_request.customer is customer
    assert catering_request in customer.requests


def test_catering_request_relationship_uses_expected_foreign_key():
    foreign_keys = list(
        CateringRequest.__table__.foreign_keys
    )

    assert len(foreign_keys) == 1

    foreign_key = foreign_keys[0]

    assert foreign_key.target_fullname == "customers.id"


def test_catering_request_uses_expected_model_types():
    catering_request = CateringRequest(
        customer_id=1,
        request_date=date(2026, 9, 28),
        requested_service="Event Catering",
        service_date=date(2026, 10, 1),
        attendance=100,
    )

    assert isinstance(catering_request.request_date, date)
    assert isinstance(catering_request.service_date, date)
    assert isinstance(catering_request.attendance, int)


def test_catering_request_soft_delete_methods_work():
    catering_request = CateringRequest(
        customer_id=1,
        request_date=date(2026, 9, 28),
        requested_service="Event Catering",
        service_date=date(2026, 10, 1),
        attendance=100,
    )

    catering_request.soft_delete()

    assert catering_request.is_deleted is True
    assert isinstance(
        catering_request.deleted_at,
        datetime,
    )

    catering_request.restore()

    assert catering_request.is_deleted is False
    assert catering_request.deleted_at is None
