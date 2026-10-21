"""
Tests for the Catering Revenue service.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityValidationException
from app.modules.catering.models import CateringRevenue
from app.modules.catering.services import CateringRevenueService
from app.modules.catering.workflows import CateringRevenueWorkflow


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def event_repository():
    return Mock()


@pytest.fixture
def quotation_repository():
    return Mock()


@pytest.fixture
def authorization_adapter():
    return Mock()


@pytest.fixture
def workflow():
    return Mock(spec=CateringRevenueWorkflow)


@pytest.fixture
def service(
    repository,
    event_repository,
    quotation_repository,
    authorization_adapter,
    workflow,
):
    return CateringRevenueService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
        event_repository=event_repository,
        quotation_repository=quotation_repository,
    )


@pytest.fixture
def revenue():
    return CateringRevenue(
        revenue_reference="REV-001",
        source_type="EVENT",
        source_reference="EVT-001",
        customer_id=3,
        event_id=7,
        amount=Decimal("250.00"),
        currency="USD",
        revenue_date=date(2026, 10, 1),
        status=CateringRevenueWorkflow.DRAFT,
    )


@pytest.fixture
def delivered_event(event_repository):
    event = Mock()
    event.id = 7
    event.customer_id = 3
    event.status = "DELIVERED"
    event_repository.get_by_id.return_value = event
    return event


@pytest.fixture
def accepted_quotation(quotation_repository):
    quotation = Mock()
    quotation.id = 12
    quotation.event_id = 7
    quotation.customer_id = 3
    quotation.total_amount = Decimal("250.00")
    quotation_repository.get_accepted_by_event_id.return_value = quotation
    return quotation


def _set_transition(workflow, target_state):
    state = Mock()
    state.name = target_state
    workflow.transition.return_value = state


def test_create_authorizes_and_persists(
    service,
    revenue,
    authorization_adapter,
    repository,
):
    service.create(revenue, subject="user")

    authorization_adapter.authorize.assert_called_once_with(
        "user",
        "CATERING.CATERING_REVENUE.CREATE",
    )
    repository.add.assert_called_once_with(revenue)


def test_create_fails_closed_without_authorization_adapter(revenue):
    service = CateringRevenueService(
        repository=Mock(),
        authorization_adapter=None,
        event_repository=Mock(),
        quotation_repository=Mock(),
    )

    with pytest.raises(RuntimeError):
        service.create(revenue, subject="user")


def test_create_rejects_non_draft_revenue(
    service,
    revenue,
    repository,
):
    revenue.status = CateringRevenueWorkflow.ELIGIBLE

    with pytest.raises(EntityValidationException):
        service.create(revenue, subject="user")

    repository.add.assert_not_called()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("revenue_reference", ""),
        ("source_type", ""),
        ("source_reference", ""),
        ("amount", None),
        ("amount", Decimal("-1.00")),
        ("currency", ""),
        ("currency", "US"),
        ("revenue_date", None),
    ],
)
def test_create_rejects_invalid_required_fields(
    service,
    revenue,
    repository,
    field,
    value,
):
    setattr(revenue, field, value)

    with pytest.raises(EntityValidationException):
        service.create(revenue, subject="user")

    repository.add.assert_not_called()


def test_establish_eligibility_records_evidence_and_transitions(
    service,
    revenue,
    authorization_adapter,
    workflow,
    repository,
    event_repository,
    quotation_repository,
    delivered_event,
    accepted_quotation,
):
    _set_transition(workflow, CateringRevenueWorkflow.ELIGIBLE)

    service.establish_eligibility(
        revenue,
        subject="user",
        delivery_evidence="Delivery confirmed by the event lead.",
        eligibility_reason="Service delivered against accepted quotation.",
    )

    authorization_adapter.authorize.assert_called_once_with(
        "user",
        "CATERING.CATERING_REVENUE.ESTABLISH_ELIGIBILITY",
    )
    event_repository.get_by_id.assert_called_once_with(7)
    quotation_repository.get_accepted_by_event_id.assert_called_once_with(7)
    workflow.transition.assert_called_once_with(
        CateringRevenueWorkflow.DRAFT,
        CateringRevenueWorkflow.ELIGIBLE,
    )
    repository.update.assert_called_once_with(revenue)

    assert revenue.status == CateringRevenueWorkflow.ELIGIBLE
    assert revenue.eligibility_quotation_id == 12
    assert revenue.delivery_evidence == (
        "Delivery confirmed by the event lead."
    )
    assert revenue.eligibility_reason == (
        "Service delivered against accepted quotation."
    )
    assert revenue.amount_adjustment_reason is None
    assert revenue.eligible_at is not None


@pytest.mark.parametrize(
    ("delivery_evidence", "eligibility_reason"),
    [
        ("", "Valid reason"),
        ("   ", "Valid reason"),
        ("Valid evidence", ""),
        ("Valid evidence", "   "),
    ],
)
def test_establish_eligibility_requires_evidence_and_reason(
    service,
    revenue,
    workflow,
    repository,
    delivered_event,
    accepted_quotation,
    delivery_evidence,
    eligibility_reason,
):
    with pytest.raises(EntityValidationException):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence=delivery_evidence,
            eligibility_reason=eligibility_reason,
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_requires_event(
    service,
    revenue,
    workflow,
    repository,
):
    revenue.event_id = None

    with pytest.raises(
        EntityValidationException,
        match="Catering Event is required",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_requires_existing_event(
    service,
    revenue,
    event_repository,
    workflow,
    repository,
):
    event_repository.get_by_id.return_value = None

    with pytest.raises(
        EntityValidationException,
        match="could not be found",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


@pytest.mark.parametrize(
    "event_status",
    [
        "REQUESTED",
        "QUOTED",
        "CONFIRMED",
        "PLANNING",
        "READY",
        "IN_PRODUCTION",
        "CANCELLED",
    ],
)
def test_establish_eligibility_rejects_event_not_delivered(
    service,
    revenue,
    delivered_event,
    event_repository,
    workflow,
    repository,
    event_status,
):
    delivered_event.status = event_status

    with pytest.raises(
        EntityValidationException,
        match="DELIVERED or COMPLETED",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_completed_event_can_establish_eligibility(
    service,
    revenue,
    delivered_event,
    workflow,
    repository,
    accepted_quotation,
):
    delivered_event.status = "COMPLETED"
    _set_transition(workflow, CateringRevenueWorkflow.ELIGIBLE)

    service.establish_eligibility(
        revenue,
        subject="user",
        delivery_evidence="Completion confirmed by event lead.",
        eligibility_reason="Completed service against accepted quotation.",
    )

    repository.update.assert_called_once_with(revenue)


def test_establish_eligibility_rejects_customer_mismatch(
    service,
    revenue,
    delivered_event,
    workflow,
    repository,
):
    delivered_event.customer_id = 99

    with pytest.raises(
        EntityValidationException,
        match="customer must match",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_requires_accepted_quotation(
    service,
    revenue,
    delivered_event,
    quotation_repository,
    workflow,
    repository,
):
    quotation_repository.get_accepted_by_event_id.return_value = None

    with pytest.raises(
        EntityValidationException,
        match="accepted quotation is required",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_rejects_quotation_customer_mismatch(
    service,
    revenue,
    delivered_event,
    accepted_quotation,
    workflow,
    repository,
):
    accepted_quotation.customer_id = 99

    with pytest.raises(
        EntityValidationException,
        match="quotation customer must match",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_requires_adjustment_reason(
    service,
    revenue,
    accepted_quotation,
    workflow,
    repository,
    delivered_event,
):
    revenue.amount = Decimal("275.00")

    with pytest.raises(
        EntityValidationException,
        match="Amount adjustment reason is required",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_records_documented_adjustment(
    service,
    revenue,
    accepted_quotation,
    workflow,
    repository,
    delivered_event,
):
    revenue.amount = Decimal("275.00")
    _set_transition(workflow, CateringRevenueWorkflow.ELIGIBLE)

    service.establish_eligibility(
        revenue,
        subject="user",
        delivery_evidence="Delivery confirmed.",
        eligibility_reason="Service delivered.",
        amount_adjustment_reason="Additional agreed service documented.",
    )

    assert revenue.eligibility_quotation_id == 12
    assert revenue.amount_adjustment_reason == (
        "Additional agreed service documented."
    )
    repository.update.assert_called_once_with(revenue)


def test_establish_eligibility_rejects_non_draft_revenue(
    service,
    revenue,
    workflow,
    repository,
    delivered_event,
    accepted_quotation,
):
    revenue.status = CateringRevenueWorkflow.ELIGIBLE

    with pytest.raises(EntityValidationException):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_establish_eligibility_does_not_persist_on_transition_failure(
    service,
    revenue,
    workflow,
    repository,
    delivered_event,
    accepted_quotation,
):
    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition"
    )

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        service.establish_eligibility(
            revenue,
            subject="user",
            delivery_evidence="Delivery confirmed.",
            eligibility_reason="Service delivered.",
        )

    repository.update.assert_not_called()
    assert revenue.eligibility_quotation_id is None
    assert revenue.eligible_at is None


def test_recognize_authorizes_and_persists(
    service,
    revenue,
    authorization_adapter,
    workflow,
    repository,
):
    revenue.status = CateringRevenueWorkflow.ELIGIBLE
    _set_transition(workflow, CateringRevenueWorkflow.RECOGNIZED)

    service.recognize(revenue, subject="user")

    authorization_adapter.authorize.assert_called_once_with(
        "user",
        "CATERING.CATERING_REVENUE.RECOGNIZE",
    )
    workflow.transition.assert_called_once_with(
        CateringRevenueWorkflow.ELIGIBLE,
        CateringRevenueWorkflow.RECOGNIZED,
    )
    repository.update.assert_called_once_with(revenue)
    assert revenue.status == CateringRevenueWorkflow.RECOGNIZED
    assert revenue.recognized_at is not None


def test_cancel_authorizes_and_persists(
    service,
    revenue,
    authorization_adapter,
    workflow,
    repository,
):
    _set_transition(workflow, CateringRevenueWorkflow.CANCELLED)

    service.cancel(revenue, subject="user")

    authorization_adapter.authorize.assert_called_once_with(
        "user",
        "CATERING.CATERING_REVENUE.CANCEL",
    )
    workflow.transition.assert_called_once_with(
        CateringRevenueWorkflow.DRAFT,
        CateringRevenueWorkflow.CANCELLED,
    )
    repository.update.assert_called_once_with(revenue)
    assert revenue.status == CateringRevenueWorkflow.CANCELLED


def test_invalid_recognition_does_not_persist(
    service,
    revenue,
    workflow,
    repository,
):
    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition"
    )

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        service.recognize(revenue, subject="user")

    repository.update.assert_not_called()
