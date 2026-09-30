"""
Catering event requirement model tests.
"""

from datetime import date

from app.modules.catering.models import (
    CateringEvent,
    EventRequirement,
)


def test_event_requirement_model_metadata():
    assert EventRequirement.__tablename__ == (
        "catering_event_requirements"
    )

    assert (
        EventRequirement.event_id.property.columns[0].nullable
        is False
    )
    assert (
        EventRequirement.description.property.columns[0].nullable
        is False
    )
    assert (
        EventRequirement.item_reference.property.columns[0].nullable
        is True
    )
    assert (
        EventRequirement.quantity.property.columns[0].nullable
        is False
    )
    assert (
        EventRequirement.unit.property.columns[0].nullable
        is False
    )
    assert (
        EventRequirement.fulfilment_type.property.columns[0].nullable
        is False
    )
    assert (
        EventRequirement.required_by_date.property.columns[0].nullable
        is True
    )
    assert (
        EventRequirement.notes.property.columns[0].nullable
        is True
    )
    assert (
        EventRequirement.status.property.columns[0].nullable
        is False
    )


def test_event_requirement_numeric_convention():
    assert str(
        EventRequirement.quantity.property.columns[0].type
    ) == "NUMERIC(18, 3)"


def test_event_requirement_status_default():
    column = EventRequirement.status.property.columns[0]

    assert column.default is not None
    assert column.default.arg == "DRAFT"


def test_event_requirement_relationship():
    assert (
        EventRequirement.event.property.mapper.class_
        is CateringEvent
    )


def test_catering_event_exposes_requirement_relationship():
    assert (
        CateringEvent.requirements.property.mapper.class_
        is EventRequirement
    )


def test_event_requirement_required_by_date_type():
    column = EventRequirement.required_by_date.property.columns[0]

    assert column.type.python_type is date


def test_event_requirement_fulfilment_type_has_no_default():
    column = EventRequirement.fulfilment_type.property.columns[0]

    assert column.default is None
