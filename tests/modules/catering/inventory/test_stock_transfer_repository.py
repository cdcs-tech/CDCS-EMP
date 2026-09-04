"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

StockTransfer repository tests.
"""

from datetime import datetime

from app.modules.catering.models import (
    InventoryLocation,
    Product,
    ProductCategory,
    StockItem,
    StockTransfer,
)
from app.modules.catering.repositories.transfer import (
    StockTransferRepository,
)


def _create_dependencies(db_session):
    """Create the Product, StockItem, and transfer location dependencies."""
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

    source = InventoryLocation(
        code="MAIN",
        name="Main Store",
    )
    destination = InventoryLocation(
        code="KITCHEN",
        name="Kitchen Store",
    )
    db_session.add_all(
        [
            source,
            destination,
        ]
    )
    db_session.flush()

    return stock_item, source, destination


def test_get_by_reference_returns_transfer(db_session):
    """Return the StockTransfer matching the supplied reference."""
    stock_item, source, destination = _create_dependencies(
        db_session
    )

    transfer = StockTransfer(
        stock_item_id=stock_item.id,
        source_location_id=source.id,
        destination_location_id=destination.id,
        quantity=5,
        reference="TRF-001",
        reason="Test stock transfer",
        status="DRAFT",
        occurred_at=datetime.utcnow(),
    )
    db_session.add(transfer)
    db_session.flush()

    repository = StockTransferRepository()

    result = repository.get_by_reference("TRF-001")

    assert result is transfer


def test_get_by_reference_returns_none_when_missing(db_session):
    """Return None when no transfer matches the supplied reference."""
    repository = StockTransferRepository()

    result = repository.get_by_reference("MISSING")

    assert result is None
