from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.modules.procurement.models import PurchaseOrder

from app.modules.procurement.models import PurchaseOrderLine
from app.modules.procurement.repositories import (
    PurchaseOrderLineRepository,
)
from app.modules.procurement.services import (
    PurchaseOrderLineService,
)


def test_purchase_order_line_service_uses_purchase_order_line_repository():
    service = PurchaseOrderLineService()

    assert isinstance(
        service.repository,
        PurchaseOrderLineRepository,
    )
    assert service.repository.model is PurchaseOrderLine


def test_purchase_order_line_service_accepts_injected_repository():
    repository = PurchaseOrderLineRepository()
    service = PurchaseOrderLineService(
        repository=repository,
    )

    assert service.repository is repository


def test_purchase_order_line_service_exposes_crud_operations():
    service = PurchaseOrderLineService()

    assert callable(service.create)
    assert callable(service.get)
    assert callable(service.update)
    assert callable(service.delete)


@pytest.mark.parametrize(
    "persisted_status",
    [
        "SUBMITTED",
        "APPROVED",
        "REJECTED",
        "CANCELLED",
    ],
)
@pytest.mark.parametrize(
    "operation",
    ["create", "update", "delete"],
)
def test_purchase_order_line_service_rejects_mutation_for_non_draft_parent(
    monkeypatch,
    persisted_status,
    operation,
):
    repository = Mock()
    service = PurchaseOrderLineService(
        repository=repository,
    )

    line = SimpleNamespace(
        id=23,
        purchase_order_id=17,
    )

    repository.get_by_id.return_value = line

    monkeypatch.setattr(
        service,
        "_get_persisted_purchase_order_status",
        lambda purchase_order_id: persisted_status,
    )

    with pytest.raises(
        ValueError,
        match="persisted status is DRAFT",
    ):
        if operation == "create":
            service.create(line)
        elif operation == "update":
            service.update(line)
        else:
            service.delete(line.id)

    repository.add.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()


@pytest.mark.parametrize(
    "operation",
    ["create", "update", "delete"],
)
def test_purchase_order_line_service_allows_mutation_for_draft_parent(
    monkeypatch,
    operation,
):
    repository = Mock()
    service = PurchaseOrderLineService(
        repository=repository,
    )

    line = SimpleNamespace(
        id=23,
        purchase_order_id=17,
    )

    repository.get_by_id.return_value = line
    repository.add.return_value = line
    repository.update.return_value = line

    monkeypatch.setattr(
        service,
        "_get_persisted_purchase_order_status",
        lambda purchase_order_id: "DRAFT",
    )

    if operation == "create":
        result = service.create(line)
        assert result is line
        repository.add.assert_called_once_with(line)

    elif operation == "update":
        result = service.update(line)
        assert result is line
        repository.update.assert_called_once_with(line)

    else:
        service.delete(line.id)
        repository.delete.assert_called_once_with(line)


def test_purchase_order_line_update_rejects_parent_reassignment(
    monkeypatch,
):
    repository = Mock()
    service = PurchaseOrderLineService(
        repository=repository,
    )

    persisted_line = SimpleNamespace(
        id=23,
        purchase_order_id=17,
    )
    repository.get_by_id.return_value = persisted_line

    updated_line = SimpleNamespace(
        id=23,
        purchase_order_id=18,
    )

    checked_parent_ids = []

    def get_persisted_status(purchase_order_id):
        checked_parent_ids.append(purchase_order_id)
        return "DRAFT"

    monkeypatch.setattr(
        service,
        "_get_persisted_purchase_order_status",
        get_persisted_status,
    )

    with pytest.raises(
        ValueError,
        match="reassignment is not permitted",
    ):
        service.update(updated_line)

    # Reassignment is rejected before status lookup or persistence.
    assert checked_parent_ids == []
    repository.update.assert_not_called()


def test_purchase_order_line_service_rejects_missing_parent(
    monkeypatch,
):
    repository = Mock()
    service = PurchaseOrderLineService(
        repository=repository,
    )

    line = SimpleNamespace(
        id=23,
        purchase_order_id=17,
    )

    monkeypatch.setattr(
        service,
        "_get_persisted_purchase_order_status",
        lambda purchase_order_id: None,
    )

    with pytest.raises(
        ValueError,
        match="Parent Purchase Order does not exist",
    ):
        service.create(line)

    repository.add.assert_not_called()
