"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement ↔ Inventory Integration

Inventory receipt provider integration with the
enterprise IntegrationService.
"""

from datetime import datetime, timezone
from decimal import Decimal

from app.core.integration import (
    IntegrationProviderRegistry,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationService,
)
from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)
from app.modules.procurement.integration.providers.inventory import (
    InventoryReceiptIntegrationProvider,
)


class FakeProduct:
    id = 10


class FakeStockItem:
    id = 20


class FakeLocation:
    id = 30


class FakeProductRepository:
    def get_by_code(self, code):
        assert code == "WATER-500ML"
        return FakeProduct()


class FakeStockItemRepository:
    def get_by_product_id(self, product_id):
        assert product_id == 10
        return FakeStockItem()


class FakeLocationRepository:
    def get_by_code(self, code):
        assert code == "MAIN"
        return FakeLocation()


class FakeMovement:
    id = 1001
    stock_item_id = 20
    location_id = 30
    quantity = Decimal("5.000")
    movement_type = "RECEIPT"
    status = "POSTED"


class FakeMovementService:
    def __init__(self):
        self.movement = None
        self.subject = None
        self.idempotency_key = None

    def post_receipt_movement(
        self,
        movement,
        *,
        subject,
        idempotency_key,
    ):
        self.movement = movement
        self.subject = subject
        self.idempotency_key = idempotency_key
        return FakeMovement()


def build_receipt():
    return PurchaseOrderReceiptRequest(
        purchase_order_reference="PO-001",
        purchase_order_line_reference="POL-001",
        stock_item_reference="WATER-500ML",
        inventory_location_reference="MAIN",
        quantity_received=Decimal("5.000"),
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
        notes="Integration service test",
    )


def build_request():
    return IntegrationRequest(
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
        payload=build_receipt(),
        metadata={
            "module": "PROCUREMENT",
            "purchase_order_id": 1,
            "operation": (
                "procurement.purchase_order.receive"
            ),
            "subject": "test-user",
        },
    )


def build_service():
    movement_service = FakeMovementService()

    provider = InventoryReceiptIntegrationProvider(
        product_repository=FakeProductRepository(),
        stock_item_repository=FakeStockItemRepository(),
        location_repository=FakeLocationRepository(),
        movement_service=movement_service,
    )

    registry = IntegrationProviderRegistry()
    registry.register(provider)

    service = IntegrationService(
        provider_registry=registry
    )

    return service, movement_service


def test_inventory_receipt_provider_executes_through_integration_service():
    service, movement_service = build_service()

    request = build_request()

    result = service.execute(request)

    assert result.success is True
    assert result.failed is False
    assert result.provider == (
        INVENTORY_INTEGRATION_PROVIDER
    )
    assert result.operation == (
        INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
    )

    assert isinstance(
        result.response,
        IntegrationResponse,
    )

    assert result.response.success is True
    assert result.response.request_id == (
        request.request_id
    )

    assert movement_service.movement is not None
    assert movement_service.subject == "test-user"


def test_inventory_receipt_provider_is_registered_by_expected_identity():
    service, _ = build_service()

    assert service.has_provider(
        INVENTORY_INTEGRATION_PROVIDER
    ) is True

    assert service.provider_count() == 1
