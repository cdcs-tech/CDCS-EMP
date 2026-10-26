"""
Tests for the Procurement Purchase Order service.
"""

from types import SimpleNamespace

import pytest

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


@pytest.mark.parametrize(
    "persisted_status",
    [
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
        "CANCELLED",
    ],
)
def test_purchase_order_service_rejects_update_when_persisted_status_is_not_draft(
    monkeypatch,
    persisted_status,
):
    repository = Mock(spec=PurchaseOrderRepository)
    service = PurchaseOrderService(repository=repository)

    purchase_order = SimpleNamespace(
        id=17,
        status="DRAFT",
    )

    monkeypatch.setattr(
        service,
        "_get_persisted_status",
        lambda purchase_order_id: persisted_status,
    )

    with pytest.raises(
        ValueError,
        match="persisted status is DRAFT",
    ):
        service.update(purchase_order)

    repository.update.assert_not_called()


def test_purchase_order_service_updates_persisted_draft_order(
    monkeypatch,
):
    repository = Mock(spec=PurchaseOrderRepository)
    purchase_order = SimpleNamespace(
        id=17,
        status="DRAFT",
    )
    repository.update.return_value = purchase_order

    service = PurchaseOrderService(repository=repository)

    monkeypatch.setattr(
        service,
        "_get_persisted_status",
        lambda purchase_order_id: "DRAFT",
    )

    result = service.update(purchase_order)

    assert result is purchase_order
    repository.update.assert_called_once_with(purchase_order)


def test_purchase_order_service_rejects_direct_status_change(
    monkeypatch,
):
    repository = Mock(spec=PurchaseOrderRepository)
    service = PurchaseOrderService(repository=repository)

    purchase_order = SimpleNamespace(
        id=17,
        status="APPROVED",
    )

    monkeypatch.setattr(
        service,
        "_get_persisted_status",
        lambda purchase_order_id: "DRAFT",
    )

    with pytest.raises(
        ValueError,
        match="status must be changed through its workflow",
    ):
        service.update(purchase_order)

    repository.update.assert_not_called()


def test_purchase_order_service_rejects_update_when_memory_status_is_draft_but_persisted_status_is_approved(
    monkeypatch,
):
    repository = Mock(spec=PurchaseOrderRepository)
    service = PurchaseOrderService(repository=repository)

    # The in-memory status is deliberately misleading.
    purchase_order = SimpleNamespace(
        id=17,
        status="DRAFT",
    )

    monkeypatch.setattr(
        service,
        "_get_persisted_status",
        lambda purchase_order_id: "APPROVED",
    )

    with pytest.raises(ValueError):
        service.update(purchase_order)

    repository.update.assert_not_called()


def test_purchase_order_service_rejects_delete_when_persisted_status_is_not_draft(
    monkeypatch,
):
    repository = Mock(spec=PurchaseOrderRepository)
    purchase_order = SimpleNamespace(
        id=17,
        status="DRAFT",
    )
    repository.get_by_id.return_value = purchase_order

    service = PurchaseOrderService(repository=repository)

    monkeypatch.setattr(
        service,
        "_get_persisted_status",
        lambda purchase_order_id: "APPROVED",
    )

    with pytest.raises(
        ValueError,
        match="persisted status is DRAFT",
    ):
        service.delete(17)

    repository.delete.assert_not_called()


def test_purchase_order_service_deletes_persisted_draft_order(
    monkeypatch,
):
    repository = Mock(spec=PurchaseOrderRepository)
    purchase_order = SimpleNamespace(
        id=17,
        status="DRAFT",
    )
    repository.get_by_id.return_value = purchase_order

    service = PurchaseOrderService(repository=repository)

    monkeypatch.setattr(
        service,
        "_get_persisted_status",
        lambda purchase_order_id: "DRAFT",
    )

    service.delete(17)

    repository.delete.assert_called_once_with(purchase_order)
