"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration

Inventory receipt integration provider tests.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.core.integration import (
    IntegrationRequest,
    IntegrationResponse,
)
from app.modules.catering.models import StockMovement
from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)
from app.modules.procurement.integration.providers.inventory import (
    InventoryReceiptIntegrationProvider,
)


class FakeProduct:
    def __init__(self, product_id: int):
        self.id = product_id


class FakeStockItem:
    def __init__(self, stock_item_id: int):
        self.id = stock_item_id


class FakeLocation:
    def __init__(self, location_id: int):
        self.id = location_id


class FakeProductRepository:
    def __init__(self, product=None):
        self.product = product
        self.requested_code = None

    def get_by_code(self, code):
        self.requested_code = code
        return self.product


class FakeStockItemRepository:
    def __init__(self, stock_item=None):
        self.stock_item = stock_item
        self.requested_product_id = None

    def get_by_product_id(self, product_id):
        self.requested_product_id = product_id
        return self.stock_item


class FakeLocationRepository:
    def __init__(self, location=None):
        self.location = location
        self.requested_code = None

    def get_by_code(self, code):
        self.requested_code = code
        return self.location


class FakeMovementService:
    def __init__(self, movement=None, error=None):
        self.movement = movement
        self.error = error
        self.received_movement = None
        self.received_subject = None
        self.received_idempotency_key = None

    def post_receipt_movement(
        self,
        movement,
        *,
        subject,
        idempotency_key,
    ):
        if self.error is not None:
            raise self.error

        self.received_movement = movement
        self.received_subject = subject
        self.received_idempotency_key = idempotency_key

        if self.movement is not None:
            return self.movement

        movement.id = 1001
        return movement


def build_receipt(
    *,
    quantity=Decimal("5.000"),
):
    return PurchaseOrderReceiptRequest(
        purchase_order_reference="PO-001",
        purchase_order_line_reference="POL-001",
        stock_item_reference="WATER-500ML",
        inventory_location_reference="MAIN",
        quantity_received=quantity,
        unit="bottle",
        received_at=datetime(
            2026,
            9,
            20,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        receiving_reference="GRN-001",
        idempotency_key="RECEIPT-001",
        notes="Initial receipt",
    )


def build_request(
    *,
    receipt=None,
    metadata=None,
):
    return IntegrationRequest(
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
        payload=receipt or build_receipt(),
        metadata=metadata or {
            "module": "PROCUREMENT",
            "purchase_order_id": 1,
            "operation": "procurement.purchase_order.receive",
            "subject": "test-user",
        },
    )


def build_provider(
    *,
    product=None,
    stock_item=None,
    location=None,
    movement_service=None,
):
    return InventoryReceiptIntegrationProvider(
        product_repository=FakeProductRepository(
            product or FakeProduct(10)
        ),
        stock_item_repository=FakeStockItemRepository(
            stock_item or FakeStockItem(20)
        ),
        location_repository=FakeLocationRepository(
            location or FakeLocation(30)
        ),
        movement_service=(
            movement_service
            or FakeMovementService()
        ),
    )


def test_provider_name():
    provider = build_provider()

    assert provider.provider_name == "inventory"


def test_provider_supports_receiving_operation():
    provider = build_provider()

    assert (
        provider.supports(
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        )
        is True
    )


def test_provider_rejects_unsupported_operation():
    provider = build_provider()

    assert provider.supports("unsupported") is False


def test_provider_validates_receipt_request():
    provider = build_provider()

    request = build_request()

    assert provider.validate(request) is None


def test_provider_requires_receipt_contract_payload():
    provider = build_provider()

    request = build_request(
        receipt="invalid payload"
    )

    with pytest.raises(
        TypeError,
        match="PurchaseOrderReceiptRequest",
    ):
        provider.validate(request)


def test_provider_requires_movement_service():
    provider = InventoryReceiptIntegrationProvider(
        product_repository=FakeProductRepository(),
        stock_item_repository=FakeStockItemRepository(),
        location_repository=FakeLocationRepository(),
        movement_service=None,
    )

    request = build_request()

    with pytest.raises(
        RuntimeError,
        match="Inventory movement service",
    ):
        provider.validate(request)


def test_provider_returns_invalid_request_response_for_invalid_payload():
    provider = build_provider()

    request = build_request(
        receipt="invalid payload"
    )

    response = provider.execute(request)

    assert isinstance(response, IntegrationResponse)
    assert response.success is False
    assert (
        response.error
        == "INVALID_INVENTORY_RECEIPT_REQUEST"
    )
    assert response.request_id == request.request_id


def test_provider_resolves_product_by_stock_item_reference():
    product = FakeProduct(10)
    product_repository = FakeProductRepository(product)

    provider = InventoryReceiptIntegrationProvider(
        product_repository=product_repository,
        stock_item_repository=FakeStockItemRepository(
            FakeStockItem(20)
        ),
        location_repository=FakeLocationRepository(
            FakeLocation(30)
        ),
        movement_service=FakeMovementService(),
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is True
    assert (
        product_repository.requested_code
        == "WATER-500ML"
    )


def test_provider_returns_product_not_found_response():
    provider = build_provider(
        product=None,
    )

    provider.product_repository.product = None

    request = build_request()

    response = provider.execute(request)

    assert response.success is False
    assert response.error == "INVENTORY_PRODUCT_NOT_FOUND"


def test_provider_returns_stock_item_not_found_response():
    stock_item_repository = FakeStockItemRepository(
        stock_item=None
    )

    provider = InventoryReceiptIntegrationProvider(
        product_repository=FakeProductRepository(
            FakeProduct(10)
        ),
        stock_item_repository=stock_item_repository,
        location_repository=FakeLocationRepository(
            FakeLocation(30)
        ),
        movement_service=FakeMovementService(),
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is False
    assert (
        response.error
        == "INVENTORY_STOCK_ITEM_NOT_FOUND"
    )


def test_provider_returns_location_not_found_response():
    location_repository = FakeLocationRepository(
        location=None
    )

    provider = InventoryReceiptIntegrationProvider(
        product_repository=FakeProductRepository(
            FakeProduct(10)
        ),
        stock_item_repository=FakeStockItemRepository(
            FakeStockItem(20)
        ),
        location_repository=location_repository,
        movement_service=FakeMovementService(),
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is False
    assert (
        response.error
        == "INVENTORY_LOCATION_NOT_FOUND"
    )


def test_provider_constructs_receipt_stock_movement():
    movement_service = FakeMovementService()

    provider = build_provider(
        movement_service=movement_service,
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is True

    movement = movement_service.received_movement

    assert isinstance(movement, StockMovement)
    assert movement.stock_item_id == 20
    assert movement.location_id == 30
    assert movement.movement_type == "RECEIPT"
    assert movement.quantity == Decimal("5.000")
    assert movement.reference == "GRN-001"
    assert (
        movement.reason
        == "Purchase Order receipt PO-001 / POL-001"
    )
    assert movement.status == "DRAFT"
    assert (
        movement.occurred_at
        == request.payload.received_at
    )


def test_provider_delegates_posting_to_movement_service():
    movement_service = FakeMovementService()

    provider = build_provider(
        movement_service=movement_service,
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is True
    assert movement_service.received_movement is not None


def test_provider_passes_authorization_subject_to_movement_service():
    movement_service = FakeMovementService()

    provider = build_provider(
        movement_service=movement_service,
    )

    request = build_request(
        metadata={
            "module": "PROCUREMENT",
            "purchase_order_id": 1,
            "operation": (
                "procurement.purchase_order.receive"
            ),
            "subject": "authorized-user",
        }
    )

    response = provider.execute(request)

    assert response.success is True
    assert (
        movement_service.received_subject
        == "authorized-user"
    )


def test_provider_returns_successful_integration_response():
    posted_movement = StockMovement(
        stock_item_id=20,
        location_id=30,
        movement_type="RECEIPT",
        quantity=Decimal("5.000"),
        reference="GRN-001",
        reason="Purchase Order receipt PO-001 / POL-001",
        status="POSTED",
        occurred_at=datetime(
            2026,
            9,
            20,
            10,
            30,
            tzinfo=timezone.utc,
        ),
    )
    posted_movement.id = 1001

    movement_service = FakeMovementService(
        movement=posted_movement
    )

    provider = build_provider(
        movement_service=movement_service,
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is True
    assert response.request_id == request.request_id
    assert response.message == (
        "Inventory receipt posted successfully."
    )
    assert response.data == {
        "stock_movement_id": 1001,
        "stock_item_id": 20,
        "location_id": 30,
        "quantity": Decimal("5.000"),
        "movement_type": "RECEIPT",
        "status": "POSTED",
        "receiving_reference": "GRN-001",
    }


def test_provider_handles_inventory_posting_failure():
    movement_service = FakeMovementService(
        error=ValueError("Posting failed.")
    )

    provider = build_provider(
        movement_service=movement_service,
    )

    request = build_request()

    response = provider.execute(request)

    assert response.success is False
    assert response.request_id == request.request_id
    assert response.message == (
        "Inventory receipt posting could not be completed."
    )
    assert response.error == "Posting failed."


def test_provider_does_not_mutate_inventory_balance_directly():
    provider = build_provider()

    assert not hasattr(
        provider,
        "balance_repository",
    )


def test_provider_does_not_mutate_inventory_movement_repository_directly():
    provider = build_provider()

    assert not hasattr(
        provider,
        "movement_repository",
    )


def test_provider_does_not_implement_receipt_idempotency():
    provider = build_provider()

    assert not hasattr(
        provider,
        "idempotency_repository",
    )
