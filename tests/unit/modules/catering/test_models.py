"""
Catering model relationship and database-constraint tests.
"""


from app.modules.catering.models import (
    Product,
    ProductCategory,
)


def test_product_category_relationship_is_bidirectional():
    """
    Product and ProductCategory must expose the
    established bidirectional ORM relationship.
    """

    assert Product.category.property.back_populates == "products"
    assert ProductCategory.products.property.back_populates == "category"


def test_product_category_foreign_key_is_required():
    """
    Product.category_id must be a required foreign key
    to product_categories.id.
    """

    column = Product.__table__.c.category_id

    assert column.nullable is False

    foreign_keys = list(column.foreign_keys)

    assert len(foreign_keys) == 1

    foreign_key = foreign_keys[0]

    assert str(foreign_key.target_fullname) == (
        "product_categories.id"
    )


def test_product_code_is_unique():
    """
    Product.code must remain uniquely constrained.
    """

    column = Product.__table__.c.code

    assert column.unique is True


def test_product_category_code_is_unique():
    """
    ProductCategory.code must remain uniquely constrained.
    """

    column = ProductCategory.__table__.c.code

    assert column.unique is True


def test_product_category_tables_have_primary_keys():
    """
    Both Catering master-data entities must retain the
    enterprise BaseModel primary-key foundation.
    """

    assert Product.__table__.primary_key.columns.keys() == ["id"]
    assert ProductCategory.__table__.primary_key.columns.keys() == [
        "id"
    ]


def test_product_category_relationship_targets_are_correct():
    """
    ORM relationships must resolve to the intended model
    classes rather than another business-domain entity.
    """

    assert Product.category.property.mapper.class_ is ProductCategory
    assert (
        ProductCategory.products.property.mapper.class_
        is Product
    )


def test_product_category_unique_constraints_are_materialized():
    """
    Both Catering master-data tables must contain a unique
    constraint covering their code column.
    """

    product_unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in Product.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    category_unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in ProductCategory.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    }

    assert ("code",) in product_unique_columns
    assert ("code",) in category_unique_columns
