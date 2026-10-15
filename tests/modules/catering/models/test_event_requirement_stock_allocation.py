"""Tests for Catering Event Requirement stock allocation model."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.modules.catering.models import (
    EventRequirementStockAllocation,
)


def _insert_allocation(**overrides):
    values = {
        "event_requirement_id": 1,
        "stock_item_id": 1,
        "location_id": 1,
        "quantity": Decimal("2.000"),
        "unit": "kg",
        "idempotency_key": "allocation-test-001",
        "status": "ACTIVE",
    }
    values.update(overrides)
    allocation = EventRequirementStockAllocation(**values)
    db.session.add(allocation)
    db.session.flush()
    return allocation


def test_allocation_table_has_expected_fields():
    columns = set(EventRequirementStockAllocation.__table__.columns.keys())

    assert {
        "event_requirement_id",
        "stock_item_id",
        "location_id",
        "quantity",
        "unit",
        "idempotency_key",
        "status",
    }.issubset(columns)


@pytest.mark.parametrize("quantity", [Decimal("0"), Decimal("-1")])
def test_allocation_rejects_non_positive_quantity(app, quantity):
    with app.app_context():
        allocation = EventRequirementStockAllocation(
            event_requirement_id=1,
            stock_item_id=1,
            location_id=1,
            quantity=quantity,
            unit="kg",
            idempotency_key=f"invalid-quantity-{quantity}",
            status="ACTIVE",
        )
        db.session.add(allocation)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()


@pytest.mark.parametrize("status", ["DRAFT", "POSTED", "INVALID"])
def test_allocation_rejects_unsupported_status(app, status):
    with app.app_context():
        allocation = EventRequirementStockAllocation(
            event_requirement_id=1,
            stock_item_id=1,
            location_id=1,
            quantity=Decimal("1.000"),
            unit="kg",
            idempotency_key=f"invalid-status-{status}",
            status=status,
        )
        db.session.add(allocation)

        with pytest.raises(IntegrityError):
            db.session.flush()

        db.session.rollback()
