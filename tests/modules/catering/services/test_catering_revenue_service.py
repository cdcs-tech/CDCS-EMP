
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
def authorization_adapter():
    return Mock()


@pytest.fixture
def workflow():
    return Mock(spec=CateringRevenueWorkflow)


@pytest.fixture
def service(repository, authorization_adapter, workflow):
    return CateringRevenueService(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )


@pytest.fixture
def revenue():
    return CateringRevenue(
        revenue_reference="REV-001",
        source_type="EVENT",
        source_reference="EVT-001",
        amount=Decimal("250.00"),
        currency="USD",
        revenue_date=date(2026, 10, 1),
        status=CateringRevenueWorkflow.DRAFT,
    )


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


def test_create_fails_closed_without_authorization_adapter(
    revenue,
):
    service = CateringRevenueService(
        repository=Mock(),
        authorization_adapter=None,
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


def test_establish_eligibility_authorizes_transitions_and_persists(
    service,
    revenue,
    authorization_adapter,
    workflow,
    repository,
):
    workflow.transition.return_value = Mock(
        name=CateringRevenueWorkflow.ELIGIBLE
    )
    workflow.transition.return_value.name = (
        CateringRevenueWorkflow.ELIGIBLE
    )

    service.establish_eligibility(revenue, subject="user")

    authorization_adapter.authorize.assert_called_once_with(
        "user",
        "CATERING.CATERING_REVENUE.ESTABLISH_ELIGIBILITY",
    )
    workflow.transition.assert_called_once_with(
        CateringRevenueWorkflow.DRAFT,
        CateringRevenueWorkflow.ELIGIBLE,
    )
    repository.update.assert_called_once_with(revenue)
    assert revenue.status == CateringRevenueWorkflow.ELIGIBLE


def test_recognize_authorizes_and_persists(
    service,
    revenue,
    authorization_adapter,
    workflow,
    repository,
):
    revenue.status = CateringRevenueWorkflow.ELIGIBLE
    workflow.transition.return_value = Mock(
        name=CateringRevenueWorkflow.RECOGNIZED
    )
    workflow.transition.return_value.name = (
        CateringRevenueWorkflow.RECOGNIZED
    )

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
    workflow.transition.return_value = Mock(
        name=CateringRevenueWorkflow.CANCELLED
    )
    workflow.transition.return_value.name = (
        CateringRevenueWorkflow.CANCELLED
    )

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
