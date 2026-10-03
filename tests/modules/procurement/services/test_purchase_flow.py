from datetime import date
from unittest.mock import MagicMock

import pytest

from app.modules.procurement.models import PurchaseOrder, PurchaseRequest
from app.modules.procurement.services.purchase_flow import (
    ProcurementPurchaseFlowService,
)


@pytest.fixture
def purchase_requirement():
    return MagicMock(
        id=101,
        reference="PRQ-CATERING-001",
    )


@pytest.fixture
def purchase_request():
    return MagicMock(
        id=202,
        reference="PR-CATERING-001",
    )


@pytest.fixture
def supplier():
    return MagicMock(
        id=303,
        reference="SUP-001",
    )


@pytest.fixture
def authorization_adapter():
    adapter = MagicMock()
    return adapter


@pytest.fixture
def purchase_requirement_repository():
    repository = MagicMock()
    return repository


@pytest.fixture
def purchase_request_repository():
    repository = MagicMock()
    return repository


@pytest.fixture
def supplier_repository():
    repository = MagicMock()
    return repository


@pytest.fixture
def purchase_request_service():
    service = MagicMock()
    return service


@pytest.fixture
def purchase_order_service():
    service = MagicMock()
    return service


@pytest.fixture
def service(
    purchase_requirement_repository,
    purchase_request_repository,
    supplier_repository,
    purchase_request_service,
    purchase_order_service,
    authorization_adapter,
):
    return ProcurementPurchaseFlowService(
        purchase_requirement_repository=purchase_requirement_repository,
        purchase_request_repository=purchase_request_repository,
        supplier_repository=supplier_repository,
        purchase_request_service=purchase_request_service,
        purchase_order_service=purchase_order_service,
        authorization_adapter=authorization_adapter,
    )


def test_create_purchase_request_from_requirement_creates_draft_parent_document(
    service,
    purchase_requirement,
    purchase_requirement_repository,
    purchase_request_service,
    authorization_adapter,
):
    purchase_requirement_repository.get_by_id.return_value = purchase_requirement
    created_request = MagicMock(id=202)
    purchase_request_service.create.return_value = created_request

    result = service.create_purchase_request_from_requirement(
        purchase_requirement,
        reference="PR-CATERING-001",
        request_date=date(2026, 10, 1),
        required_by_date=date(2026, 10, 3),
        justification="Catering event requirement",
        notes="C6.3 validation",
        subject="test-user",
    )

    assert result is created_request

    authorization_adapter.authorize.assert_called_once_with(
        "test-user",
        service.PURCHASE_REQUEST_CREATE,
    )
    purchase_requirement_repository.get_by_id.assert_called_once_with(
        purchase_requirement.id,
    )

    created = purchase_request_service.create.call_args.args[0]

    assert isinstance(created, PurchaseRequest)
    assert created.reference == "PR-CATERING-001"
    assert created.purchase_requirement_id == purchase_requirement.id
    assert created.request_date == date(2026, 10, 1)
    assert created.required_by_date == date(2026, 10, 3)
    assert created.status == "DRAFT"
    assert created.justification == "Catering event requirement"
    assert created.notes == "C6.3 validation"


def test_create_purchase_request_from_requirement_requires_authorization(
    service,
    purchase_requirement,
    authorization_adapter,
    purchase_requirement_repository,
    purchase_request_service,
):
    authorization_adapter.authorize.side_effect = PermissionError(
        "not authorized",
    )

    with pytest.raises(PermissionError, match="not authorized"):
        service.create_purchase_request_from_requirement(
            purchase_requirement,
            reference="PR-CATERING-001",
            request_date=date(2026, 10, 1),
            subject="test-user",
        )

    authorization_adapter.authorize.assert_called_once_with(
        "test-user",
        service.PURCHASE_REQUEST_CREATE,
    )
    purchase_requirement_repository.get_by_id.assert_not_called()
    purchase_request_service.create.assert_not_called()


def test_create_purchase_order_from_request_creates_draft_parent_document(
    service,
    purchase_request,
    purchase_request_repository,
    supplier_repository,
    purchase_order_service,
    authorization_adapter,
    supplier,
):
    purchase_request_repository.get_by_id.return_value = purchase_request
    supplier_repository.get_by_id.return_value = supplier

    created_order = MagicMock(id=404)
    purchase_order_service.create.return_value = created_order

    result = service.create_purchase_order_from_request(
        purchase_request,
        reference="PO-CATERING-001",
        supplier_id=supplier.id,
        order_date=date(2026, 10, 2),
        expected_delivery_date=date(2026, 10, 4),
        subject="test-user",
    )

    assert result is created_order

    authorization_adapter.authorize.assert_called_once_with(
        "test-user",
        service.PURCHASE_ORDER_CREATE,
    )
    purchase_request_repository.get_by_id.assert_called_once_with(
        purchase_request.id,
    )
    supplier_repository.get_by_id.assert_called_once_with(
        supplier.id,
    )

    created = purchase_order_service.create.call_args.args[0]

    assert isinstance(created, PurchaseOrder)
    assert created.reference == "PO-CATERING-001"
    assert created.supplier_id == supplier.id
    assert created.order_date == date(2026, 10, 2)
    assert created.expected_delivery_date == date(2026, 10, 4)
    assert created.status == "DRAFT"
    assert created.purchase_request_id == purchase_request.id


def test_create_purchase_order_from_request_requires_authorization(
    service,
    purchase_request,
    authorization_adapter,
    purchase_request_repository,
    supplier_repository,
    purchase_order_service,
):
    authorization_adapter.authorize.side_effect = PermissionError(
        "not authorized",
    )

    with pytest.raises(PermissionError, match="not authorized"):
        service.create_purchase_order_from_request(
            purchase_request,
            reference="PO-CATERING-001",
            supplier_id=303,
            order_date=date(2026, 10, 2),
            subject="test-user",
        )

    authorization_adapter.authorize.assert_called_once_with(
        "test-user",
        service.PURCHASE_ORDER_CREATE,
    )
    purchase_request_repository.get_by_id.assert_not_called()
    supplier_repository.get_by_id.assert_not_called()
    purchase_order_service.create.assert_not_called()


def test_create_purchase_order_from_request_requires_existing_supplier(
    service,
    purchase_request,
    purchase_request_repository,
    supplier_repository,
    purchase_order_service,
):
    purchase_request_repository.get_by_id.return_value = purchase_request
    supplier_repository.get_by_id.return_value = None

    with pytest.raises(Exception):
        service.create_purchase_order_from_request(
            purchase_request,
            reference="PO-CATERING-001",
            supplier_id=999,
            order_date=date(2026, 10, 2),
            subject="test-user",
        )

    purchase_request_repository.get_by_id.assert_called_once_with(
        purchase_request.id,
    )
    supplier_repository.get_by_id.assert_called_once_with(999)
    purchase_order_service.create.assert_not_called()


def test_purchase_request_composition_does_not_execute_workflow_transition(
    service,
    purchase_requirement,
    purchase_requirement_repository,
    purchase_request_service,
):
    purchase_requirement_repository.get_by_id.return_value = purchase_requirement

    service.create_purchase_request_from_requirement(
        purchase_requirement,
        reference="PR-CATERING-001",
        request_date=date(2026, 10, 1),
        subject="test-user",
    )

    purchase_request_service.create.assert_called_once()

    # The flow coordinator delegates persistence only. Workflow submission
    # and approval remain separate PurchaseRequestService operations.
    purchase_request_service.submit.assert_not_called()
    purchase_request_service.approve.assert_not_called()


def test_purchase_order_composition_does_not_execute_workflow_transition(
    service,
    purchase_request,
    purchase_request_repository,
    supplier_repository,
    purchase_order_service,
    supplier,
):
    purchase_request_repository.get_by_id.return_value = purchase_request
    supplier_repository.get_by_id.return_value = supplier

    service.create_purchase_order_from_request(
        purchase_request,
        reference="PO-CATERING-001",
        supplier_id=supplier.id,
        order_date=date(2026, 10, 2),
        subject="test-user",
    )

    purchase_order_service.create.assert_called_once()

    # The flow coordinator delegates persistence only. Purchase Order
    # workflow transitions remain separate operations.
    purchase_order_service.submit.assert_not_called()
    purchase_order_service.approve.assert_not_called()
