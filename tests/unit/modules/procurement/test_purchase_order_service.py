"""
Tests for the Procurement Purchase Order service.
"""

from unittest.mock import Mock

from app.core.data import QueryOptions
from app.modules.procurement.models import PurchaseOrder
from app.modules.procurement.repositories import (
    PurchaseOrderRepository,
)
from app.modules.procurement.services import (
    PurchaseOrderService,
)


def test_purchase_order_repository_uses_purchase_order_model():
    repository = PurchaseOrderRepository()

    assert repository.model is PurchaseOrder


def test_purchase_order_service_uses_default_repository():
    service = PurchaseOrderService()

    assert isinstance(
        service.repository,
        PurchaseOrderRepository,
    )


def test_purchase_order_service_accepts_repository():
    repository = Mock(spec=PurchaseOrderRepository)

    service = PurchaseOrderService(
        repository=repository,
    )

    assert service.repository is repository


def test_purchase_order_service_paginate_delegates_to_repository():
    repository = Mock(spec=PurchaseOrderRepository)
    expected = object()

    repository.paginate.return_value = expected

    service = PurchaseOrderService(
        repository=repository,
    )

    options = QueryOptions()

    result = service.paginate(options)

    assert result is expected
    repository.paginate.assert_called_once_with(options)


def test_purchase_order_service_is_crud_service():
    service = PurchaseOrderService()

    assert hasattr(service, "create")
    assert hasattr(service, "get")
    assert hasattr(service, "update")
    assert hasattr(service, "delete")
