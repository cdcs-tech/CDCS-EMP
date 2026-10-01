"""
Catering Expense Cost Association model tests.
"""

from datetime import datetime, timezone

from app.modules.catering.models import (
    CateringExpenseCostAssociation,
)


def build_association():

    return CateringExpenseCostAssociation(
        expense_id=901,
        catering_context_type="CATERING_EVENT",
        catering_context_reference="EVENT-2026-001",
        status="ELIGIBLE",
        contribution_id=(
            "expense:901:catering:event:EVENT-2026-001"
        ),
    )


def test_association_stores_external_expense_reference():

    association = build_association()

    assert association.expense_id == 901


def test_association_stores_catering_context():

    association = build_association()

    assert (
        association.catering_context_type
        == "CATERING_EVENT"
    )

    assert (
        association.catering_context_reference
        == "EVENT-2026-001"
    )


def test_association_declares_eligible_database_default():

    column = (
        CateringExpenseCostAssociation.__table__.columns[
            "status"
        ]
    )

    assert column.default is not None
    assert column.default.arg == "ELIGIBLE"


def test_association_stores_stable_contribution_id():

    association = build_association()

    assert (
        association.contribution_id
        == "expense:901:catering:event:EVENT-2026-001"
    )


def test_mark_consumed_updates_consumption_state():

    association = build_association()

    consumed_at = datetime(
        2026,
        10,
        1,
        10,
        30,
        tzinfo=timezone.utc,
    )

    association.mark_consumed(
        consumed_at
    )

    assert association.status == "CONSUMED"

    assert (
        association.consumed_at
        == consumed_at
    )


def test_mark_consumed_is_idempotent():

    association = build_association()

    first_consumed_at = datetime(
        2026,
        10,
        1,
        10,
        30,
        tzinfo=timezone.utc,
    )

    second_consumed_at = datetime(
        2026,
        10,
        1,
        11,
        30,
        tzinfo=timezone.utc,
    )

    association.mark_consumed(
        first_consumed_at
    )

    association.mark_consumed(
        second_consumed_at
    )

    assert association.status == "CONSUMED"

    assert (
        association.consumed_at
        == first_consumed_at
    )
