"""
Procurement service integration and dependency-injection tests.
"""

import pytest

from app.core.crud import CRUDService
from app.core.crud.exceptions import (
    EntityNotFoundException,
)
from app.modules.procurement.models import Supplier
from app.modules.procurement.repositories import SupplierRepository
from app.modules.procurement.services import SupplierService


def test_supplier_service_uses_supplier_repository():
    """
    SupplierService must be backed by SupplierRepository.
    """

    repository = SupplierRepository()

    service = SupplierService(
        repository=repository,
    )

    assert isinstance(
        service,
        CRUDService,
    )

    assert service.repository is repository
    assert service.repository.model is Supplier


def test_supplier_service_creates_default_repository():
    """
    SupplierService creates its standard repository when
    no dependency is explicitly supplied.
    """

    service = SupplierService()

    assert isinstance(
        service.repository,
        SupplierRepository,
    )

    assert service.repository.model is Supplier


def test_supplier_service_create_delegates_to_repository(
    db_session,
):
    """
    SupplierService creation must use the injected repository.
    """

    repository = SupplierRepository()

    service = SupplierService(
        repository=repository,
    )

    supplier = Supplier(
        name="ABC Supplies",
        code="SUP-001",
        supplier_type="GENERAL",
        status="ACTIVE",
    )

    result = service.create(
        supplier
    )

    assert result is supplier

    assert repository.get_by_id(
        supplier.id
    ) is supplier


def test_supplier_service_get_missing_entity_raises(
    db_session,
):
    """
    SupplierService must preserve the generic CRUD
    not-found contract.
    """

    service = SupplierService()

    with pytest.raises(
        EntityNotFoundException,
    ):
        service.get(
            999999
        )


def test_supplier_service_public_import_boundary():
    """
    SupplierService must be exposed through the Procurement
    services package.
    """

    from app.modules.procurement.services import (
        SupplierService as Imported,
    )

    assert Imported is SupplierService
