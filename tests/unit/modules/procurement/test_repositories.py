"""
Procurement repository integration tests.
"""

from app.core.data.repository import BaseRepository
from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.procurement.models import Supplier
from app.modules.procurement.repositories import SupplierRepository


def test_supplier_repository_uses_enterprise_sqlalchemy_repository():
    """
    SupplierRepository must use the enterprise SQLAlchemy
    repository implementation.
    """

    repository = SupplierRepository()

    assert isinstance(
        repository,
        SQLAlchemyRepository,
    )

    assert isinstance(
        repository,
        BaseRepository,
    )

    assert repository.model is Supplier


def test_supplier_repository_is_module_local():
    """
    SupplierRepository must remain within the Procurement
    module boundary.
    """

    assert (
        SupplierRepository.__module__
        == "app.modules.procurement.repositories.supplier"
    )


def test_supplier_repository_public_import_boundary():
    """
    SupplierRepository must be exposed through the Procurement
    repositories package.
    """

    from app.modules.procurement.repositories import (
        SupplierRepository as Imported,
    )

    assert Imported is SupplierRepository
