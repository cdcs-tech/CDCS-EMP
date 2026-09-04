"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

StockMovement repository tests.
"""

from datetime import datetime

from app.modules.catering.models import (
    InventoryLocation,
    Product,
    ProductCategory,
    StockItem,
    StockMovement,
)
from app.modules.catering.repositories.movement import (
    StockMovementRepository,
)


def _create_dependencies(db_session):
    """Create the Product, StockItem, and Location dependencies."""
    category = ProductCategory(
        name="Test Category",
        code="CAT-001",
    )
    db_session.add(category)
    db_session.flush()

    product = Product(
        category_id=category.id,
        name="Test Product",
        code="PROD-001",
        unit="kg",
    )
    db_session.add(product)
    db_session.flush()

    stock_item = StockItem(
        product_id=product.id,
    )
    db_session.add(stock_item)
    db_session.flush()

    location = InventoryLocation(
        code="MAIN",
        name="Main Store",
    )
    db_session.add(location)
    db_session.flush()

    return stock_item, location


def test_get_by_reference_returns_movement(db_session):
    """Return the StockMovement matching the supplied reference."""
    stock_item, location = _create_dependencies(db_session)

    movement = StockMovement(
        stock_item_id=stock_item.id,
        location_id=location.id,
        movement_type="RECEIPT",
        quantity=10,
        reference="GRN-001",
        reason="Initial test receipt",
        status="DRAFT",
        occurred_at=datetime.utcnow(),
    )
    db_session.add(movement)
    db_session.flush()

    repository = StockMovementRepository()

    result = repository.get_by_reference("GRN-001")

    assert result is movement


def test_get_by_reference_returns_none_when_missing(db_session):
    """Return None when no movement matches the supplied reference."""
    repository = StockMovementRepository()

    result = repository.get_by_reference("MISSING")

    assert result is None
