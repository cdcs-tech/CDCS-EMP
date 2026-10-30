from contextlib import contextmanager
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import app.modules.catering.services.catering_event_consumption as consumption_module
from app.core.crud.exceptions import EntityNotFoundException, EntityValidationException
from app.modules.catering.services.catering_event_consumption import (
    CateringEventConsumptionService,
)


class FakeMovement:
    next_id = 1

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = None
        self.status = "DRAFT"
        self.posted_at = None


class FakeEvidence:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.id = None
        self.is_deleted = False


class FakeTransactionManager:
    def __init__(self):
        self.calls = 0
        self.exceptions = []

    @contextmanager
    def transaction(self):
        self.calls += 1
        try:
            yield
        except Exception as exc:
            self.exceptions.append(exc)
            raise


class FakeMovementRepository:
    def __init__(self):
        self.items = {}
        self.next_id = 1

    def add(self, movement):
        movement.id = self.next_id
        self.next_id += 1
        self.items[movement.id] = movement
        return movement

    def update(self, movement):
        self.items[movement.id] = movement
        return movement

    def get_by_idempotency_key(self, idempotency_key):
        return next(
            (
                item
                for item in self.items
                if item.idempotency_key == idempotency_key
            ),
            None,
        )


class FakeEvidenceRepository:
    def __init__(self):
        self.items = []
        self.fail_on_add = False

    def get_by_requirement_id(self, requirement_id):
        return [
            item
            for item in self.items
            if item.event_requirement_id == requirement_id
            and not item.is_deleted
        ]

    def get_by_idempotency_key(self, idempotency_key):
        return next(
            (
                item
                for item in self.items
                if getattr(item, "idempotency_key", None) == idempotency_key
            ),
            None,
        )

    def add(self, evidence):
        if self.fail_on_add:
            raise RuntimeError("Evidence persistence failed.")

        evidence.id = len(self.items) + 1
        self.items.append(evidence)
        return evidence


class FakeMovementService:
    def __init__(self):
        self.repository = FakeMovementRepository()
        self.transaction_manager = FakeTransactionManager()
        self.authorization_adapter = Mock()
        self._authorize = Mock()
        self._validate_movement_for_posting = Mock()
        self._validate_workflow_transition = Mock()
        self._apply_balance_effect = Mock()

    def get_by_reference(self, reference):
        return next(
            (
                item
                for item in self.repository.items.values()
                if item.reference == reference
            ),
            None,
        )


@pytest.fixture
def setup_service(monkeypatch):
    monkeypatch.setattr(
        consumption_module,
        "StockMovement",
        FakeMovement,
    )
    monkeypatch.setattr(
        consumption_module,
        "CateringEventConsumptionEvidence",
        FakeEvidence,
    )

    event = SimpleNamespace(id=12)
    requirement = SimpleNamespace(
        id=34,
        guid="requirement-guid",
        event_id=12,
        is_deleted=False,
        status="READY",
        stock_item_id=56,
        quantity=Decimal("10.000"),
        unit="kg",
    )

    requirement_repository = Mock()
    requirement_repository.get_by_id.return_value = requirement
    requirement_repository.get_by_id_for_update.return_value = requirement

    evidence_repository = FakeEvidenceRepository()
    movement_service = FakeMovementService()

    service = CateringEventConsumptionService(
        requirement_repository=requirement_repository,
        consumption_evidence_repository=evidence_repository,
        movement_service=movement_service,
    )

    def consume(**overrides):
        args = {
            "event": event,
            "requirement_id": requirement.id,
            "location_id": 78,
            "quantity": Decimal("3.000"),
            "unit": "kg",
            "subject": object(),
            "idempotency_key": "issue-001",
        }
        args.update(overrides)
        return service.consume(**args)

    return SimpleNamespace(
        event=event,
        requirement=requirement,
        requirement_repository=requirement_repository,
        evidence_repository=evidence_repository,
        movement_service=movement_service,
        service=service,
        consume=consume,
    )


def test_consume_posts_issue_and_persists_evidence(setup_service):
    ctx = setup_service

    def assert_draft_before_transition(movement):
        assert movement.status == "DRAFT"

    ctx.movement_service._validate_workflow_transition.side_effect = (
        assert_draft_before_transition
    )

    evidence = ctx.consume()

    movement = ctx.movement_service.repository.items[
        evidence.stock_movement_id
    ]

    assert movement.movement_type == "ISSUE"
    assert movement.quantity == Decimal("-3.000")
    assert movement.unit == ctx.requirement.unit
    assert movement.status == "POSTED"
    assert evidence.event_requirement_id == ctx.requirement.id
    assert evidence.quantity == Decimal("3.000")
    assert evidence.unit == "kg"
    assert evidence.idempotency_key == "issue-001"

    ctx.movement_service._authorize.assert_called_once_with(
        ctx.service.movement_service._authorize.call_args.args[0],
        "CATERING.STOCK_MOVEMENT.POST",
    )
    ctx.movement_service._apply_balance_effect.assert_called_once_with(
        movement
    )
    assert ctx.movement_service.transaction_manager.calls == 1
    ctx.requirement_repository.get_by_id_for_update.assert_called_once_with(
        ctx.requirement.id
    )


def test_consume_rejects_requirement_owned_by_another_event(setup_service):
    ctx = setup_service
    ctx.requirement.event_id = 999

    with pytest.raises(
        EntityValidationException,
        match="does not belong",
    ):
        ctx.consume()

    assert ctx.movement_service.transaction_manager.calls == 0


def test_consume_rejects_missing_requirement(setup_service):
    ctx = setup_service
    ctx.requirement_repository.get_by_id.return_value = None

    with pytest.raises(EntityNotFoundException):
        ctx.consume()

    assert ctx.movement_service.transaction_manager.calls == 0


@pytest.mark.parametrize("status", ["DRAFT", "CANCELLED"])
def test_consume_rejects_ineligible_requirement(setup_service, status):
    ctx = setup_service
    ctx.requirement.status = status

    with pytest.raises(EntityValidationException, match="not eligible"):
        ctx.consume()

    assert ctx.movement_service.transaction_manager.calls == 0


def test_consume_rejects_mismatched_unit(setup_service):
    ctx = setup_service

    with pytest.raises(EntityValidationException, match="unit"):
        ctx.consume(unit="litres")

    assert ctx.movement_service.transaction_manager.calls == 0


@pytest.mark.parametrize("quantity", [0, -1, "not-a-number", "NaN", "Infinity"])
def test_consume_rejects_invalid_quantity(setup_service, quantity):
    ctx = setup_service

    with pytest.raises(EntityValidationException):
        ctx.consume(quantity=quantity)

    assert ctx.movement_service.transaction_manager.calls == 0


def test_consume_rejects_quantity_above_requirement(setup_service):
    ctx = setup_service

    with pytest.raises(EntityValidationException, match="exceed"):
        ctx.consume(quantity=Decimal("10.001"))

    assert ctx.movement_service.transaction_manager.calls == 0


def test_consume_rejects_cumulative_overconsumption(setup_service):
    ctx = setup_service
    ctx.evidence_repository.items.append(
        FakeEvidence(
            event_requirement_id=ctx.requirement.id,
            stock_movement_id=900,
            quantity=Decimal("8.000"),
            unit="kg",
        )
    )

    with pytest.raises(EntityValidationException, match="exceed"):
        ctx.consume(quantity=Decimal("3.000"))

    assert ctx.movement_service.transaction_manager.calls == 0


def test_consume_retry_returns_existing_evidence(setup_service):
    ctx = setup_service

    first = ctx.consume()
    second = ctx.consume()

    assert second is first
    assert len(ctx.evidence_repository.items) == 1
    assert len(ctx.movement_service.repository.items) == 1
    assert ctx.movement_service.transaction_manager.calls == 1


def test_consume_full_quantity_retry_returns_existing_evidence(setup_service):
    ctx = setup_service

    first = ctx.consume(quantity=Decimal("10.000"))
    second = ctx.consume(quantity=Decimal("10.000"))

    assert second is first
    assert len(ctx.evidence_repository.items) == 1
    assert len(ctx.movement_service.repository.items) == 1
    assert ctx.movement_service.transaction_manager.calls == 1


def test_consume_rejects_reused_key_with_different_quantity(setup_service):
    ctx = setup_service
    ctx.consume()

    with pytest.raises(EntityValidationException, match="already used"):
        ctx.consume(quantity=Decimal("4.000"))

    assert len(ctx.evidence_repository.items) == 1
    assert len(ctx.movement_service.repository.items) == 1


def test_evidence_failure_propagates_inside_transaction(setup_service):
    ctx = setup_service
    ctx.evidence_repository.fail_on_add = True

    with pytest.raises(
        RuntimeError,
        match="Evidence persistence failed",
    ):
        ctx.consume()

    assert ctx.movement_service.transaction_manager.calls == 1
    assert len(ctx.movement_service.transaction_manager.exceptions) == 1
    assert len(ctx.evidence_repository.items) == 0
