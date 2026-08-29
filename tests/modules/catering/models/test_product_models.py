"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Focused tests for ProductCategory and Product models.
"""

from datetime import datetime

from app.modules.catering.models import (
    Product,
    ProductCategory,
)


def test_product_category_has_expected_table_and_columns():
    assert ProductCategory.__tablename__ == "product_categories"

    assert ProductCategory.id is not None
    assert ProductCategory.guid is not None

    assert ProductCategory.name.property.columns[0].nullable is False
    assert ProductCategory.code.property.columns[0].nullable is False
    assert ProductCategory.description.property.columns[0].nullable is True
    assert ProductCategory.is_active.property.columns[0].nullable is False

    assert ProductCategory.code.property.columns[0].unique is True


def test_product_category_inherits_enterprise_mixins():
    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    assert hasattr(category, "created_at")
    assert hasattr(category, "updated_at")
    assert hasattr(category, "created_by")
    assert hasattr(category, "updated_by")

    assert ProductCategory.is_deleted.property.columns[0].default.arg is False
    assert ProductCategory.is_active.property.columns[0].default.arg is True


def test_product_has_expected_table_and_columns():
    assert Product.__tablename__ == "products"

    assert Product.id is not None
    assert Product.guid is not None

    assert Product.category_id.property.columns[0].nullable is False
    assert Product.name.property.columns[0].nullable is False
    assert Product.code.property.columns[0].nullable is False
    assert Product.description.property.columns[0].nullable is True
    assert Product.unit.property.columns[0].nullable is False
    assert Product.is_active.property.columns[0].nullable is False

    assert Product.code.property.columns[0].unique is True


def test_product_inherits_enterprise_mixins():
    product = Product(
        category_id=1,
        name="Bottled Water",
        code="WATER-500ML",
        unit="bottle",
    )

    assert hasattr(product, "created_at")
    assert hasattr(product, "updated_at")
    assert hasattr(product, "created_by")
    assert hasattr(product, "updated_by")

    assert Product.is_deleted.property.columns[0].default.arg is False
    assert Product.is_active.property.columns[0].default.arg is True


def test_product_category_relationship_is_bidirectional():
    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    product = Product(
        name="Bottled Water",
        code="WATER-500ML",
        unit="bottle",
    )

    product.category = category

    assert product.category is category
    assert product in category.products


def test_product_category_relationship_uses_expected_foreign_key():
    foreign_keys = list(
        Product.__table__.foreign_keys
    )

    assert len(foreign_keys) == 1

    foreign_key = foreign_keys[0]

    assert foreign_key.target_fullname == (
        "product_categories.id"
    )
    assert foreign_key.ondelete == None


def test_product_category_soft_delete_methods_work():
    category = ProductCategory(
        name="Beverages",
        code="BEV",
    )

    category.soft_delete()

    assert category.is_deleted is True
    assert isinstance(
        category.deleted_at,
        datetime,
    )

    category.restore()

    assert category.is_deleted is False
    assert category.deleted_at is None


def test_product_soft_delete_methods_work():
    product = Product(
        category_id=1,
        name="Bottled Water",
        code="WATER-500ML",
        unit="bottle",
    )

    product.soft_delete()

    assert product.is_deleted is True
    assert isinstance(
        product.deleted_at,
        datetime,
    )

    product.restore()

    assert product.is_deleted is False
    assert product.deleted_at is None
