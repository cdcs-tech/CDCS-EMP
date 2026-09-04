"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

StockItem repository tests.
"""

from app.modules.catering.models import (
    Product,
    ProductCategory,
    StockItem,
)
from app.modules.catering.repositories.stock_item import StockItemRepository


def _create_product(db_session, code="PROD-001"):
    """Create a valid Catering Product with its required category."""
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

    return product


def test_get_by_product_id_returns_stock_item(db_session):
    """Return the StockItem associated with the supplied Product."""
    product = _create_product(db_session)

    stock_item = StockItem(
        product_id=product.id,
    )
    db_session.add(stock_item)
    db_session.flush()

    repository = StockItemRepository()

    result = repository.get_by_product_id(product.id)

    assert result is stock_item


def test_get_by_product_id_returns_none_when_missing(db_session):
    """Return None when no StockItem exists for the supplied Product."""
    repository = StockItemRepository()

    result = repository.get_by_product_id(999999)

    assert result is None


def test_exists_for_product_returns_true_when_present(db_session):
    """Return True when a StockItem exists for the supplied Product."""
    product = _create_product(db_session)

    stock_item = StockItem(
        product_id=product.id,
    )
    db_session.add(stock_item)
    db_session.flush()

    repository = StockItemRepository()

    assert repository.exists_for_product(product.id) is True


def test_exists_for_product_returns_false_when_missing(db_session):
    """Return False when no StockItem exists for the supplied Product."""
    repository = StockItemRepository()

    assert repository.exists_for_product(999999) is False
