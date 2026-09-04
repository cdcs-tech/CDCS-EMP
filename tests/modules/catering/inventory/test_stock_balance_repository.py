"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

StockBalance repository tests.
"""

from app.modules.catering.models import (
    InventoryLocation,
    Product,
    ProductCategory,
    StockBalance,
    StockItem,
)
from app.modules.catering.repositories.balance import StockBalanceRepository


def _create_stock_item(db_session, code="PROD-001"):
    """Create a valid Product and StockItem dependency chain."""
    category = ProductCategory(
        name="Test Category",
        code=f"CAT-{code}",
    )
    db_session.add(category)
    db_session.flush()

    product = Product(
        category_id=category.id,
        name="Test Product",
        code=code,
        unit="kg",
    )
    db_session.add(product)
    db_session.flush()

    stock_item = StockItem(
        product_id=product.id,
    )
    db_session.add(stock_item)
    db_session.flush()

    return stock_item


def _create_location(db_session, code="MAIN"):
    """Create a valid InventoryLocation."""
    location = InventoryLocation(
        code=code,
        name="Main Store",
    )
    db_session.add(location)
    db_session.flush()

    return location


def test_get_by_stock_item_and_location_returns_balance(db_session):
    """Return the balance for a StockItem at a specific location."""
    stock_item = _create_stock_item(db_session)
    location = _create_location(db_session)

    balance = StockBalance(
        stock_item_id=stock_item.id,
        location_id=location.id,
        quantity=25,
    )
    db_session.add(balance)
    db_session.flush()

    repository = StockBalanceRepository()

    result = repository.get_by_stock_item_and_location(
        stock_item.id,
        location.id,
    )

    assert result is balance


def test_get_by_stock_item_and_location_returns_none_when_missing(
    db_session,
):
    """Return None when no balance exists for the item/location pair."""
    stock_item = _create_stock_item(db_session)
    location = _create_location(db_session)

    repository = StockBalanceRepository()

    result = repository.get_by_stock_item_and_location(
        stock_item.id,
        location.id,
    )

    assert result is None


def test_get_by_stock_item_returns_all_balances(db_session):
    """Return all balances belonging to a StockItem."""
    stock_item = _create_stock_item(db_session)

    location_main = _create_location(db_session, code="MAIN")
    location_kitchen = _create_location(
        db_session,
        code="KITCHEN",
    )

    balance_main = StockBalance(
        stock_item_id=stock_item.id,
        location_id=location_main.id,
        quantity=25,
    )
    balance_kitchen = StockBalance(
        stock_item_id=stock_item.id,
        location_id=location_kitchen.id,
        quantity=10,
    )

    db_session.add_all(
        [
            balance_main,
            balance_kitchen,
        ]
    )
    db_session.flush()

    repository = StockBalanceRepository()

    result = repository.get_by_stock_item(stock_item.id)

    assert len(result) == 2
    assert {balance.id for balance in result} == {
        balance_main.id,
        balance_kitchen.id,
    }


def test_get_by_location_returns_all_balances(db_session):
    """Return all balances belonging to an InventoryLocation."""
    stock_item_main = _create_stock_item(
        db_session,
        code="PROD-001",
    )
    stock_item_kitchen = _create_stock_item(
        db_session,
        code="PROD-002",
    )

    location = _create_location(db_session)

    balance_main = StockBalance(
        stock_item_id=stock_item_main.id,
        location_id=location.id,
        quantity=25,
    )
    balance_kitchen = StockBalance(
        stock_item_id=stock_item_kitchen.id,
        location_id=location.id,
        quantity=10,
    )

    db_session.add_all(
        [
            balance_main,
            balance_kitchen,
        ]
    )
    db_session.flush()

    repository = StockBalanceRepository()

    result = repository.get_by_location(location.id)

    assert len(result) == 2
    assert {balance.id for balance in result} == {
        balance_main.id,
        balance_kitchen.id,
    }
