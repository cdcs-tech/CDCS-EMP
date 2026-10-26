"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Tests for the C2 Procurement purchase-flow coordinator.

The coordinator is responsible only for progressing existing Procurement
documents:

    PurchaseRequirement -> PurchaseRequest
    PurchaseRequest -> PurchaseOrder

Workflow execution and downstream integrations remain outside this service.
"""

from datetime import date
from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseRequest,
    PurchaseRequirement,
)
from app.modules.procurement.repositories import (
    PurchaseRequirementRepository,
    PurchaseRequestRepository,
    SupplierRepository,
)
from app.modules.procurement.services import (
    PurchaseOrderService,
    PurchaseRequestService,
)
from app.modules.procurement.services.purchase_flow import (
    ProcurementPurchaseFlowService,
)


def _purchase_requirement(requirement_id: int = 10):
    return Mock(
        spec=PurchaseRequirement,
        id=requirement_id,
    )


def _purchase_request(request_id: int = 20):
    return Mock(
        spec=PurchaseRequest,
        id=request_id,
    )


def _supplier(supplier_id: int = 30):
    return Mock(
        id=supplier_id,
    )


def _service():
    purchase_requirement_repository = Mock(
        spec=PurchaseRequirementRepository,
    )
    purchase_request_repository = Mock(
        spec=PurchaseRequestRepository,
    )
    supplier_repository = Mock(
        spec=SupplierRepository,
    )
    purchase_request_service = Mock(
        spec=PurchaseRequestService,
    )
    purchase_order_service = Mock(
        spec=PurchaseOrderService,
    )
    authorization_adapter = Mock()

    service = ProcurementPurchaseFlowService(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        purchase_request_repository=(
            purchase_request_repository
        ),
        supplier_repository=supplier_repository,
        purchase_request_service=purchase_request_service,
        purchase_order_service=purchase_order_service,
        authorization_adapter=authorization_adapter,
    )

    return (
        service,
        purchase_requirement_repository,
        purchase_request_repository,
        supplier_repository,
        purchase_request_service,
        purchase_order_service,
        authorization_adapter,
    )


def test_create_purchase_request_from_requirement_authorizes_and_creates_draft():
    (
        service,
        requirement_repository,
        _,
        _,
        purchase_request_service,
        _,
        authorization_adapter,
    ) = _service()

    requirement = _purchase_requirement(10)
    requirement_repository.get_by_id.return_value = requirement

    created_request = Mock(
        spec=PurchaseRequest,
    )
    purchase_request_service.create.return_value = created_request

    result = service.create_purchase_request_from_requirement(
        requirement,
        reference="PR-001",
        request_date=date(2026, 9, 29),
        required_by_date=date(2026, 10, 1),
        justification="Catering event procurement",
        notes="Pilot requirement",
        subject=42,
    )

    authorization_adapter.authorize.assert_called_once_with(
        42,
        service.PURCHASE_REQUEST_CREATE,
    )

    requirement_repository.get_by_id.assert_called_once_with(10)

    purchase_request_service.create.assert_called_once()
    created_entity = (
        purchase_request_service.create.call_args.args[0]
    )

    assert isinstance(created_entity, PurchaseRequest)
    assert created_entity.reference == "PR-001"
    assert created_entity.purchase_requirement_id == 10
    assert created_entity.request_date == date(2026, 9, 29)
    assert created_entity.required_by_date == date(2026, 10, 1)
    assert created_entity.status == "DRAFT"
    assert created_entity.justification == (
        "Catering event procurement"
    )
    assert created_entity.notes == "Pilot requirement"

    assert result is created_request


def test_create_purchase_request_from_requirement_uses_existing_requirement():
    (
        service,
        requirement_repository,
        _,
        _,
        purchase_request_service,
        _,
        _,
    ) = _service()

    requirement = _purchase_requirement(55)
    requirement_repository.get_by_id.return_value = requirement

    purchase_request_service.create.side_effect = (
        lambda entity: entity
    )

    result = service.create_purchase_request_from_requirement(
        requirement,
        reference="PR-055",
        request_date=date(2026, 9, 29),
        subject=42,
    )

    assert result.purchase_requirement_id == 55
    requirement_repository.get_by_id.assert_called_once_with(55)


def test_create_purchase_request_from_requirement_requires_existing_requirement():
    (
        service,
        requirement_repository,
        _,
        _,
        purchase_request_service,
        _,
        authorization_adapter,
    ) = _service()

    requirement = _purchase_requirement(999)
    requirement_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityNotFoundException,
        match="PurchaseRequirement",
    ):
        service.create_purchase_request_from_requirement(
            requirement,
            reference="PR-999",
            request_date=date(2026, 9, 29),
            subject=42,
        )

    authorization_adapter.authorize.assert_called_once()
    purchase_request_service.create.assert_not_called()


def test_create_purchase_request_from_requirement_requires_identifier():
    (
        service,
        requirement_repository,
        _,
        _,
        purchase_request_service,
        _,
        _,
    ) = _service()

    requirement = Mock(
        spec=PurchaseRequirement,
    )
    requirement.id = None

    with pytest.raises(
        EntityNotFoundException,
        match="PurchaseRequirement",
    ):
        service.create_purchase_request_from_requirement(
            requirement,
            reference="PR-NONE",
            request_date=date(2026, 9, 29),
            subject=42,
        )

    requirement_repository.get_by_id.assert_not_called()
    purchase_request_service.create.assert_not_called()


def test_create_purchase_request_from_requirement_does_not_execute_workflow():
    (
        service,
        requirement_repository,
        _,
        _,
        purchase_request_service,
        _,
        _,
    ) = _service()

    requirement = _purchase_requirement(10)
    requirement_repository.get_by_id.return_value = requirement
    purchase_request_service.create.side_effect = (
        lambda entity: entity
    )

    result = service.create_purchase_request_from_requirement(
        requirement,
        reference="PR-010",
        request_date=date(2026, 9, 29),
        subject=42,
    )

    assert result.status == "DRAFT"
    purchase_request_service.create.assert_called_once()

    # C2 creates the next Procurement document but does not
    # execute Purchase Request workflow transitions.
    assert not purchase_request_service.submit.called
    assert not purchase_request_service.approve.called
    assert not purchase_request_service.reject.called


def test_create_purchase_order_from_request_authorizes_and_creates_draft():
    (
        service,
        _,
        purchase_request_repository,
        supplier_repository,
        _,
        purchase_order_service,
        authorization_adapter,
    ) = _service()

    purchase_request = _purchase_request(20)
    supplier = _supplier(30)

    purchase_request_repository.get_by_id.return_value = (
        purchase_request
    )
    supplier_repository.get_by_id.return_value = supplier

    created_order = Mock(
        spec=PurchaseOrder,
    )
    purchase_order_service.create.return_value = created_order

    result = service.create_purchase_order_from_request(
        purchase_request,
        reference="PO-001",
        currency="USD",
        supplier_id=30,
        order_date=date(2026, 9, 29),
        expected_delivery_date=date(2026, 10, 2),
        subject=42,
    )

    authorization_adapter.authorize.assert_called_once_with(
        42,
        service.PURCHASE_ORDER_CREATE,
    )

    purchase_request_repository.get_by_id.assert_called_once_with(
        20,
    )
    supplier_repository.get_by_id.assert_called_once_with(
        30,
    )

    purchase_order_service.create.assert_called_once()
    created_entity = (
        purchase_order_service.create.call_args.args[0]
    )

    assert isinstance(created_entity, PurchaseOrder)
    assert created_entity.reference == "PO-001"
    assert created_entity.supplier_id == 30
    assert created_entity.order_date == date(2026, 9, 29)
    assert created_entity.expected_delivery_date == date(2026, 10, 2)
    assert created_entity.status == "DRAFT"
    assert created_entity.purchase_request_id == 20

    assert result is created_order


def test_create_purchase_order_from_request_requires_existing_request():
    (
        service,
        _,
        purchase_request_repository,
        _,
        _,
        purchase_order_service,
        _,
    ) = _service()

    purchase_request = _purchase_request(999)
    purchase_request_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityNotFoundException,
        match="PurchaseRequest",
    ):
        service.create_purchase_order_from_request(
            purchase_request,
            reference="PO-999",
            currency="USD",
            supplier_id=30,
            order_date=date(2026, 9, 29),
            subject=42,
        )

    purchase_order_service.create.assert_not_called()


def test_create_purchase_order_from_request_requires_identifier():
    (
        service,
        _,
        purchase_request_repository,
        _,
        _,
        purchase_order_service,
        _,
    ) = _service()

    purchase_request = Mock(
        spec=PurchaseRequest,
    )
    purchase_request.id = None

    with pytest.raises(
        EntityNotFoundException,
        match="PurchaseRequest",
    ):
        service.create_purchase_order_from_request(
            purchase_request,
            reference="PO-NONE",
            currency="USD",
            supplier_id=30,
            order_date=date(2026, 9, 29),
            subject=42,
        )

    purchase_request_repository.get_by_id.assert_not_called()
    purchase_order_service.create.assert_not_called()


def test_create_purchase_order_from_request_requires_existing_supplier():
    (
        service,
        _,
        purchase_request_repository,
        supplier_repository,
        _,
        purchase_order_service,
        _,
    ) = _service()

    purchase_request = _purchase_request(20)

    purchase_request_repository.get_by_id.return_value = (
        purchase_request
    )
    supplier_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityNotFoundException,
        match="Supplier",
    ):
        service.create_purchase_order_from_request(
            purchase_request,
            reference="PO-020",
            currency="USD",
            supplier_id=999,
            order_date=date(2026, 9, 29),
            subject=42,
        )

    supplier_repository.get_by_id.assert_called_once_with(
        999,
    )
    purchase_order_service.create.assert_not_called()


def test_create_purchase_order_from_request_does_not_execute_workflow():
    (
        service,
        _,
        purchase_request_repository,
        supplier_repository,
        _,
        purchase_order_service,
        _,
    ) = _service()

    purchase_request = _purchase_request(20)
    supplier = _supplier(30)

    purchase_request_repository.get_by_id.return_value = (
        purchase_request
    )
    supplier_repository.get_by_id.return_value = supplier
    purchase_order_service.create.side_effect = (
        lambda entity: entity
    )

    result = service.create_purchase_order_from_request(
        purchase_request,
        reference="PO-020",
        currency="USD",
        supplier_id=30,
        order_date=date(2026, 9, 29),
        subject=42,
    )

    assert result.status == "DRAFT"
    purchase_order_service.create.assert_called_once()

    # C2 creates the next Procurement document but does not
    # execute Purchase Order workflow transitions.
    assert not purchase_order_service.submit.called
    assert not purchase_order_service.approve.called
    assert not purchase_order_service.reject.called


def test_purchase_request_creation_uses_existing_service():
    (
        service,
        requirement_repository,
        _,
        _,
        purchase_request_service,
        _,
        _,
    ) = _service()

    requirement = _purchase_requirement(10)
    requirement_repository.get_by_id.return_value = requirement

    purchase_request_service.create.side_effect = (
        lambda entity: entity
    )

    result = service.create_purchase_request_from_requirement(
        requirement,
        reference="PR-SERVICE",
        request_date=date(2026, 9, 29),
        subject=42,
    )

    assert isinstance(result, PurchaseRequest)
    purchase_request_service.create.assert_called_once()


def test_purchase_order_creation_uses_existing_service():
    (
        service,
        _,
        purchase_request_repository,
        supplier_repository,
        _,
        purchase_order_service,
        _,
    ) = _service()

    purchase_request = _purchase_request(20)
    supplier = _supplier(30)

    purchase_request_repository.get_by_id.return_value = (
        purchase_request
    )
    supplier_repository.get_by_id.return_value = supplier

    purchase_order_service.create.side_effect = (
        lambda entity: entity
    )

    result = service.create_purchase_order_from_request(
        purchase_request,
        reference="PO-SERVICE",
        currency="USD",
        supplier_id=30,
        order_date=date(2026, 9, 29),
        subject=42,
    )

    assert isinstance(result, PurchaseOrder)
    purchase_order_service.create.assert_called_once()
