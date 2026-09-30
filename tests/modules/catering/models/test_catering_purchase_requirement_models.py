"""
Catering purchase requirement model tests.
"""

from datetime import date

from app.modules.catering.models import (
    CateringPurchaseRequirement,
    EventRequirement,
)


def test_catering_purchase_requirement_model_metadata():
    assert CateringPurchaseRequirement.__tablename__ == (
        "catering_purchase_requirements"
    )

    assert (
        CateringPurchaseRequirement.event_requirement_id
        .property.columns[0]
        .nullable
        is False
    )
    assert (
        CateringPurchaseRequirement.description.property.columns[0]
        .nullable
        is False
    )
    assert (
        CateringPurchaseRequirement.item_reference.property.columns[0]
        .nullable
        is True
    )
    assert (
        CateringPurchaseRequirement.quantity.property.columns[0]
        .nullable
        is False
    )
    assert (
        CateringPurchaseRequirement.unit.property.columns[0]
        .nullable
        is False
    )
    assert (
        CateringPurchaseRequirement.required_by_date.property.columns[0]
        .nullable
        is True
    )
    assert (
        CateringPurchaseRequirement.justification.property.columns[0]
        .nullable
        is True
    )
    assert (
        CateringPurchaseRequirement.status.property.columns[0]
        .nullable
        is False
    )
    assert (
        CateringPurchaseRequirement.procurement_reference
        .property.columns[0]
        .nullable
        is True
    )


def test_catering_purchase_requirement_numeric_convention():
    assert str(
        CateringPurchaseRequirement.quantity.property.columns[0].type
    ) == "NUMERIC(18, 3)"


def test_catering_purchase_requirement_status_default():
    column = CateringPurchaseRequirement.status.property.columns[0]

    assert column.default is not None
    assert column.default.arg == "DRAFT"


def test_catering_purchase_requirement_event_requirement_relationship():
    assert (
        CateringPurchaseRequirement.event_requirement.property.mapper.class_
        is EventRequirement
    )


def test_event_requirement_exposes_purchase_requirement_relationship():
    assert (
        EventRequirement.purchase_requirement.property.mapper.class_
        is CateringPurchaseRequirement
    )


def test_catering_purchase_requirement_relationship_is_one_to_one():
    relationship = EventRequirement.purchase_requirement.property

    assert relationship.uselist is False


def test_catering_purchase_requirement_required_by_date_type():
    column = (
        CateringPurchaseRequirement.required_by_date
        .property
        .columns[0]
    )

    assert column.type.python_type is date


def test_catering_purchase_requirement_procurement_reference_has_no_foreign_key():
    column = (
        CateringPurchaseRequirement.procurement_reference
        .property
        .columns[0]
    )

    assert column.foreign_keys == set()


def test_catering_purchase_requirement_event_requirement_id_is_unique():
    column = (
        CateringPurchaseRequirement.event_requirement_id
        .property
        .columns[0]
    )

    assert column.unique is True
