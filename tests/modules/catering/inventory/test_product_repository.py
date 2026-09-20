"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Inventory

Product repository tests.
"""

from app.modules.catering.models import (
    Product,
    ProductCategory,
)
from app.modules.catering.repositories.product import (
    ProductRepository,
)


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


def test_get_by_code_returns_product(db_session):
    """Return the Product associated with the supplied business code."""
    product = _create_product(db_session)

    repository = ProductRepository()

    result = repository.get_by_code(product.code)

    assert result is product


def test_get_by_code_returns_none_when_missing(db_session):
    """Return None when no Product exists for the supplied business code."""
    repository = ProductRepository()

    result = repository.get_by_code("MISSING-PRODUCT")

    assert result is None
