"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

InventoryLocation repository tests.
"""

from app.modules.catering.models import InventoryLocation
from app.modules.catering.repositories.location import (
    InventoryLocationRepository,
)


def test_get_by_code_returns_location(db_session):
    """Return the InventoryLocation matching the supplied code."""
    location = InventoryLocation(
        code="MAIN",
        name="Main Store",
    )
    db_session.add(location)
    db_session.flush()

    repository = InventoryLocationRepository()

    result = repository.get_by_code("MAIN")

    assert result is location


def test_get_by_code_returns_none_when_missing(db_session):
    """Return None when no location matches the supplied code."""
    repository = InventoryLocationRepository()

    result = repository.get_by_code("MISSING")

    assert result is None
