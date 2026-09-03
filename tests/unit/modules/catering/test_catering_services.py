"""
Catering service integration and dependency-injection tests.
"""

import pytest

from app.core.crud import CRUDService
from app.core.crud.exceptions import (
    EntityNotFoundException,
)
from app.modules.catering.models import (
    Product,
    ProductCategory,
)
from app.modules.catering.repositories import (
    ProductRepository,
    ProductCategoryRepository,
)
from app.modules.catering.services import (
    ProductService,
    ProductCategoryService,
)

from unittest.mock import Mock

from app.core.data import PaginatedResult, QueryOptions


def test_product_service_uses_product_repository():
    """
    ProductService must be backed by ProductRepository.
    """

    repository = ProductRepository()

    service = ProductService(
        repository=repository,
    )

    assert isinstance(
        service,
        CRUDService,
    )

    assert service.repository is repository
    assert service.repository.model is Product


def test_product_category_service_uses_product_category_repository():
    """
    ProductCategoryService must be backed by ProductCategoryRepository.
    """

    repository = ProductCategoryRepository()

    service = ProductCategoryService(
        repository=repository,
    )

    assert isinstance(
        service,
        CRUDService,
    )

    assert service.repository is repository
    assert service.repository.model is ProductCategory


def test_product_service_creates_default_repository():
    """
    ProductService creates its standard repository when
    no dependency is explicitly supplied.
    """

    service = ProductService()

    assert isinstance(
        service.repository,
        ProductRepository,
    )

    assert service.repository.model is Product


def test_product_category_service_creates_default_repository():
    """
    ProductCategoryService creates its standard repository
    when no dependency is explicitly supplied.
    """

    service = ProductCategoryService()

    assert isinstance(
        service.repository,
        ProductCategoryRepository,
    )

    assert (
        service.repository.model
        is ProductCategory
    )


def test_product_service_create_delegates_to_repository(
    db_session,
):
    """
    ProductService creation must use the injected repository.
    """

    category = ProductCategory(
        name="Dry Goods",
        code="DRY-001",
    )

    db_session.add(category)
    db_session.flush()

    repository = ProductRepository()

    service = ProductService(
        repository=repository,
    )

    product = Product(
        category_id=category.id,
        name="Rice",
        code="RICE-001",
        unit="kg",
    )

    result = service.create(
        product
    )

    assert result is product

    assert repository.get_by_id(
        product.id
    ) is product


def test_product_category_service_create_delegates_to_repository(db_session):
    """
    ProductCategoryService creation must use the injected repository.
    """

    repository = ProductCategoryRepository()
    service = ProductCategoryService(
        repository=repository,
    )

    category = ProductCategory(
        name="Dry Goods",
        code="DRY-001",
    )

    result = service.create(
        category
    )

    assert result is category
    assert repository.get_by_id(
        category.id
    ) is category


def test_product_service_get_missing_entity_raises(db_session):
    """
    ProductService must preserve the generic CRUD not-found contract.
    """

    service = ProductService()

    with pytest.raises(
        EntityNotFoundException,
    ):
        service.get(
            999999
        )


def test_product_category_service_get_missing_entity_raises(db_session):
    """
    ProductCategoryService must preserve the generic CRUD
    not-found contract.
    """

    service = ProductCategoryService()

    with pytest.raises(
        EntityNotFoundException,
    ):
        service.get(
            999999
        )


def test_product_service_public_import_boundary():
    """
    ProductService must be exposed through the Catering
    services package.
    """

    from app.modules.catering.services import ProductService as Imported

    assert Imported is ProductService


def test_product_category_service_public_import_boundary():
    """
    ProductCategoryService must be exposed through the Catering
    services package.
    """

    from app.modules.catering.services import (
        ProductCategoryService as Imported,
    )

    assert Imported is ProductCategoryService

def test_product_service_paginate_delegates_to_repository():
    """
    ProductService pagination must delegate to the injected repository.
    """

    repository = Mock(
        spec=ProductRepository,
    )

    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=2,
        page_size=10,
    )

    repository.paginate.return_value = expected

    service = ProductService(
        repository=repository,
    )

    options = QueryOptions(
        page=2,
        page_size=10,
        sort_by="name",
        sort_direction="asc",
    )

    result = service.paginate(
        options
    )

    assert result is expected

    repository.paginate.assert_called_once_with(
        options
    )


def test_product_category_service_paginate_delegates_to_repository():
    """
    ProductCategoryService pagination must delegate to
    the injected repository.
    """

    repository = Mock(
        spec=ProductCategoryRepository,
    )

    expected = PaginatedResult(
        items=[],
        total_records=0,
        page=2,
        page_size=10,
    )

    repository.paginate.return_value = expected

    service = ProductCategoryService(
        repository=repository,
    )

    options = QueryOptions(
        page=2,
        page_size=10,
        sort_by="name",
        sort_direction="asc",
    )

    result = service.paginate(
        options
    )

    assert result is expected

    repository.paginate.assert_called_once_with(
        options
    )

