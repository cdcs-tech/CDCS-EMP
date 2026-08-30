"""
Catering repository integration tests.
"""

from app.core.data.repository import BaseRepository
from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.catering.models import (
    Product,
    ProductCategory,
)

from app.modules.catering.repositories import (
    ProductRepository,
    ProductCategoryRepository,
)


def test_product_repository_uses_enterprise_sqlalchemy_repository():
    """
    ProductRepository must use the enterprise SQLAlchemy
    repository implementation.
    """

    repository = ProductRepository()

    assert isinstance(
        repository,
        SQLAlchemyRepository,
    )

    assert isinstance(
        repository,
        BaseRepository,
    )

    assert repository.model is Product


def test_product_category_repository_uses_enterprise_sqlalchemy_repository():
    """
    ProductCategoryRepository must use the enterprise SQLAlchemy
    repository implementation.
    """

    repository = ProductCategoryRepository()

    assert isinstance(
        repository,
        SQLAlchemyRepository,
    )

    assert isinstance(
        repository,
        BaseRepository,
    )

    assert repository.model is ProductCategory


def test_catering_repositories_are_module_local():
    """
    Catering repositories must remain within the Catering
    module boundary rather than the global data framework.
    """

    assert (
        ProductRepository.__module__
        == "app.modules.catering.repositories.product"
    )

    assert (
        ProductCategoryRepository.__module__
        == "app.modules.catering.repositories.product_category"
    )
