"""
Focused tests for Procurement ↔ Inventory receipt idempotency.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.integration import IntegrationRequest
from app.modules.catering.models.inventory_receipt_idempotency import (
    InventoryReceiptIdempotency,
)
from app.modules.catering.models.stock_movement import StockMovement
from app.modules.catering.services.movement import StockMovementService
from app.modules.procurement.integration import (
    INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    PurchaseOrderReceiptRequest,
)
from app.modules.procurement.integration.providers.inventory import (
    InventoryReceiptIntegrationProvider,
)


class FakeTransactionManager:
    """
    Minimal transaction-manager test double.

    The production transaction manager remains responsible for
    actual commit/rollback behavior.
    """

    @contextmanager
    def transaction(self):
        yield


class FakeMovementRepository:
    def __init__(self) -> None:
        self.movements = []

    def add(self, movement):
        movement.id = len(self.movements) + 1
        self.movements.append(movement)
        return movement

    def update(self, movement):
        return movement

    def paginate(self, options):
        raise NotImplementedError

    def get_by_reference(self, reference):
        for movement in self.movements:
            if movement.reference == reference:
                return movement

        return None


class FakeBalanceRepository:
    def __init__(self) -> None:
        self.balances = {}

    def get_by_stock_item_and_location(
        self,
        stock_item_id,
        location_id,
    ):
        return self.balances.get(
            (stock_item_id, location_id)
        )

    def add(self, balance):
        self.balances[
            (
                balance.stock_item_id,
                balance.location_id,
            )
        ] = balance

        return balance

    def update(self, balance):
        self.balances[
            (
                balance.stock_item_id,
                balance.location_id,
            )
        ] = balance

        return balance


class FakeIdempotencyRepository:
    def __init__(self) -> None:
        self.records = {}

    def get_by_idempotency_key(
        self,
        idempotency_key,
    ):
        return self.records.get(
            idempotency_key
        )

    def add(self, record):
        self.records[
            record.idempotency_key
        ] = record

        return record


class AllowAllAuthorizationAdapter:
    def authorize(
        self,
        subject,
        permission_code,
    ):
        return True


class AllowPostingWorkflow:
    def transition(
        self,
        current_state,
        target_state,
    ):
        return target_state


def build_service():
    movement_repository = FakeMovementRepository()
    balance_repository = FakeBalanceRepository()
    idempotency_repository = FakeIdempotencyRepository()

    service = StockMovementService(
        repository=movement_repository,
        transaction_manager=FakeTransactionManager(),
        balance_repository=balance_repository,
        authorization_adapter=(
            AllowAllAuthorizationAdapter()
        ),
        workflow=AllowPostingWorkflow(),
        idempotency_repository=(
            idempotency_repository
        ),
    )

    return (
        service,
        movement_repository,
        balance_repository,
        idempotency_repository,
    )


def build_receipt(
    *,
    quantity: str = "5",
    receiving_reference: str = "GRN-001",
    idempotency_key: str = "receipt-001",
):
    return PurchaseOrderReceiptRequest(
        purchase_order_reference="PO-001",
        purchase_order_line_reference="POL-001",
        stock_item_reference="ITEM-001",
        inventory_location_reference="MAIN",
        quantity_received=Decimal(quantity),
        unit="PCS",
        received_at=datetime.now(
            timezone.utc
        ),
        receiving_reference=receiving_reference,
        idempotency_key=idempotency_key,
    )


def build_movement(
    *,
    quantity: str = "5",
    reference: str = "GRN-001",
):
    return StockMovement(
        stock_item_id=1,
        location_id=1,
        movement_type="RECEIPT",
        quantity=Decimal(quantity),
        reference=reference,
        reason="Purchase Order receipt",
        status="DRAFT",
        occurred_at=datetime.now(
            timezone.utc
        ),
    )


def test_same_idempotency_key_returns_original_movement_without_new_stock_effect():
    (
        service,
        movement_repository,
        balance_repository,
        idempotency_repository,
    ) = build_service()

    first = build_movement(
        quantity="5",
        reference="GRN-001",
    )

    first_posted = service.post_receipt_movement(
        first,
        subject="user-1",
        idempotency_key="receipt-001",
    )

    original_balance = balance_repository.balances[
        (1, 1)
    ].quantity

    second = build_movement(
        quantity="5",
        reference="GRN-002",
    )

    second_posted = service.post_receipt_movement(
        second,
        subject="user-1",
        idempotency_key="receipt-001",
    )

    assert second_posted.id == first_posted.id

    assert (
        balance_repository.balances[
            (1, 1)
        ].quantity
        == original_balance
    )

    assert len(movement_repository.movements) == 1
    assert len(idempotency_repository.records) == 1


def test_different_idempotency_keys_create_independent_receipts():
    (
        service,
        movement_repository,
        balance_repository,
        idempotency_repository,
    ) = build_service()

    first = build_movement(
        quantity="5",
        reference="GRN-001",
    )

    second = build_movement(
        quantity="3",
        reference="GRN-002",
    )

    first_posted = service.post_receipt_movement(
        first,
        subject="user-1",
        idempotency_key="receipt-001",
    )

    second_posted = service.post_receipt_movement(
        second,
        subject="user-1",
        idempotency_key="receipt-002",
    )

    assert first_posted.id != second_posted.id

    assert (
        balance_repository.balances[
            (1, 1)
        ].quantity
        == Decimal("8")
    )

    assert len(movement_repository.movements) == 2
    assert len(idempotency_repository.records) == 2


def test_failed_receipt_posting_does_not_create_idempotency_record():
    (
        service,
        movement_repository,
        balance_repository,
        idempotency_repository,
    ) = build_service()

    def failing_balance_effect(
        movement,
    ):
        raise ValueError(
            "Simulated Inventory posting failure."
        )

    service._apply_balance_effect = (
        failing_balance_effect
    )

    movement = build_movement()

    with pytest.raises(
        ValueError,
        match="Simulated Inventory posting failure",
    ):
        service.post_receipt_movement(
            movement,
            subject="user-1",
            idempotency_key="receipt-failed",
        )

    assert (
        "receipt-failed"
        not in idempotency_repository.records
    )


def test_blank_idempotency_key_is_rejected():
    (
        service,
        _movement_repository,
        _balance_repository,
        _idempotency_repository,
    ) = build_service()

    movement = build_movement()

    with pytest.raises(
        ValueError,
        match="idempotency key is required",
    ):
        service.post_receipt_movement(
            movement,
            subject="user-1",
            idempotency_key="   ",
        )


def test_provider_forwards_idempotency_key_to_inventory_service():
    product_repository = Mock()

    product = SimpleNamespace(
        id=11,
        code="ITEM-001",
    )

    product_repository.get_by_code.return_value = product

    stock_item_repository = Mock()

    stock_item = SimpleNamespace(
        id=22,
    )

    stock_item_repository.get_by_product_id.return_value = (
        stock_item
    )

    location_repository = Mock()

    location = SimpleNamespace(
        id=33,
    )

    location_repository.get_by_code.return_value = (
        location
    )

    posted_movement = SimpleNamespace(
        id=44,
        stock_item_id=22,
        location_id=33,
        quantity=Decimal("5"),
        movement_type="RECEIPT",
        status="POSTED",
    )

    movement_service = Mock()

    movement_service.post_receipt_movement.return_value = (
        posted_movement
    )

    provider = InventoryReceiptIntegrationProvider(
        product_repository=product_repository,
        stock_item_repository=stock_item_repository,
        location_repository=location_repository,
        movement_service=movement_service,
    )

    receipt = build_receipt(
        quantity="5",
        receiving_reference="GRN-001",
        idempotency_key="receipt-001",
    )

    request = IntegrationRequest(
        provider="inventory",
        operation=(
            INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION
        ),
        payload=receipt,
        metadata={
            "subject": "user-1",
        },
    )

    response = provider.execute(
        request
    )

    assert response.success is True

    movement_service.post_receipt_movement.assert_called_once()

    _, kwargs = (
        movement_service
        .post_receipt_movement
        .call_args
    )

    assert kwargs["subject"] == "user-1"
    assert kwargs["idempotency_key"] == "receipt-001"
