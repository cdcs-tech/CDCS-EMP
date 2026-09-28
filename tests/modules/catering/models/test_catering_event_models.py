"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Focused tests for the CateringEvent model.
"""

from datetime import date, datetime

from app.modules.catering.models import (
    CateringEvent,
    CateringRequest,
    Customer,
)


def test_catering_event_has_expected_table_and_columns():
    assert CateringEvent.__tablename__ == "catering_events"

    assert CateringEvent.id is not None
    assert CateringEvent.guid is not None

    assert CateringEvent.request_id.property.columns[0].nullable is False
    assert CateringEvent.customer_id.property.columns[0].nullable is False
    assert CateringEvent.event_date.property.columns[0].nullable is False
    assert CateringEvent.service_details.property.columns[0].nullable is False
    assert CateringEvent.attendance.property.columns[0].nullable is False
    assert CateringEvent.operational_notes.property.columns[0].nullable is True
    assert CateringEvent.status.property.columns[0].nullable is False


def test_catering_event_has_expected_field_lengths():
    assert (
        CateringEvent.service_details.property.columns[0].type.length
        == 1000
    )
    assert (
        CateringEvent.operational_notes.property.columns[0].type.length
        == 1000
    )
    assert CateringEvent.status.property.columns[0].type.length == 30


def test_catering_event_has_expected_date_type():
    assert (
        CateringEvent.event_date.property.columns[0].type.python_type
        is date
    )


def test_catering_event_has_expected_controlled_value_constraints():
    constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in CateringEvent.__table__.constraints
        if constraint.name
        in {
            "ck_catering_events_attendance_positive",
            "ck_catering_events_status",
        }
    }

    assert "ck_catering_events_attendance_positive" in constraints
    assert "attendance > 0" in constraints[
        "ck_catering_events_attendance_positive"
    ]

    assert "ck_catering_events_status" in constraints

    status_constraint = constraints["ck_catering_events_status"]

    for status in (
        "REQUESTED",
        "QUOTED",
        "PENDING_CONFIRMATION",
        "CONFIRMED",
        "PLANNING",
        "READY",
        "IN_PRODUCTION",
        "DELIVERED",
        "COMPLETED",
        "CANCELLED",
    ):
        assert status in status_constraint


def test_catering_event_inherits_enterprise_mixins():
    catering_event = CateringEvent(
        request_id=1,
        customer_id=1,
        event_date=date(2026, 10, 15),
        service_details="Corporate lunch service",
        attendance=50,
    )

    assert hasattr(catering_event, "created_at")
    assert hasattr(catering_event, "updated_at")
    assert hasattr(catering_event, "created_by")
    assert hasattr(catering_event, "updated_by")

    assert CateringEvent.is_deleted.property.columns[0].default.arg is False


def test_catering_event_has_expected_default_status():
    status_column = CateringEvent.status.property.columns[0]

    assert status_column.default.arg == "REQUESTED"


def test_catering_event_accepts_expected_values():
    catering_event = CateringEvent(
        request_id=10,
        customer_id=20,
        event_date=date(2026, 10, 15),
        service_details="Corporate lunch service for conference participants.",
        attendance=150,
        operational_notes="Delivery and service at the conference venue.",
        status="CONFIRMED",
    )

    assert catering_event.request_id == 10
    assert catering_event.customer_id == 20
    assert catering_event.event_date == date(2026, 10, 15)
    assert catering_event.service_details == (
        "Corporate lunch service for conference participants."
    )
    assert catering_event.attendance == 150
    assert catering_event.operational_notes == (
        "Delivery and service at the conference venue."
    )
    assert catering_event.status == "CONFIRMED"


def test_catering_event_request_relationship_is_bidirectional():
    request = CateringRequest(
        customer_id=1,
        request_date=date(2026, 9, 28),
        requested_service="Corporate Catering",
        service_date=date(2026, 10, 15),
        attendance=50,
    )

    catering_event = CateringEvent(
        request=request,
        customer_id=1,
        event_date=date(2026, 10, 15),
        service_details="Corporate lunch service",
        attendance=50,
    )

    assert catering_event.request is request
    assert catering_event in request.events


def test_catering_event_customer_relationship_is_bidirectional():
    customer = Customer(
        name="Example Customer",
        customer_type="ORGANIZATION",
    )

    catering_event = CateringEvent(
        customer=customer,
        request_id=1,
        event_date=date(2026, 10, 15),
        service_details="Corporate lunch service",
        attendance=50,
    )

    assert catering_event.customer is customer
    assert catering_event in customer.events


def test_catering_event_uses_expected_foreign_keys():
    foreign_keys = list(
        CateringEvent.__table__.foreign_keys
    )

    assert len(foreign_keys) == 2

    targets = {
        foreign_key.target_fullname
        for foreign_key in foreign_keys
    }

    assert targets == {
        "catering_requests.id",
        "customers.id",
    }


def test_catering_event_uses_expected_model_types():
    catering_event = CateringEvent(
        request_id=1,
        customer_id=1,
        event_date=date(2026, 10, 1),
        service_details="Event Catering",
        attendance=100,
    )

    assert isinstance(catering_event.event_date, date)
    assert isinstance(catering_event.attendance, int)


def test_catering_event_soft_delete_methods_work():
    catering_event = CateringEvent(
        request_id=1,
        customer_id=1,
        event_date=date(2026, 10, 1),
        service_details="Event Catering",
        attendance=100,
    )

    catering_event.soft_delete()

    assert catering_event.is_deleted is True
    assert isinstance(
        catering_event.deleted_at,
        datetime,
    )

    catering_event.restore()

    assert catering_event.is_deleted is False
    assert catering_event.deleted_at is None
