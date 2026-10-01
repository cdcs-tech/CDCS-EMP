"""
Tests for the Catering Expense Cost Consumption service.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.modules.catering.integration.contracts import (
    ApprovedExpenseCostContribution,
)
from app.modules.catering.models import (
    CateringExpenseCostAssociation,
)
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.services import (
    CateringExpenseCostConsumptionService,
)


def _contribution(
    contribution_id: str = "expense-17-catering-event-1",
) -> ApprovedExpenseCostContribution:
    """Build a valid approved Expense contribution."""

    return ApprovedExpenseCostContribution(
        expense_id=17,
        description="Catering supplies",
        amount=Decimal("125.50"),
        expense_date=date(2026, 9, 30),
        classification_reference="CATERING_SUPPLIES",
        catering_context_type="EVENT",
        catering_context_reference="EVENT-1",
        approved_at=datetime(
            2026,
            9,
            30,
            12,
            30,
            tzinfo=timezone.utc,
        ),
        contribution_id=contribution_id,
    )


def test_service_uses_default_repository():
    """Verify the service creates its default repository."""

    service = CateringExpenseCostConsumptionService()

    assert isinstance(
        service.repository,
        CateringExpenseCostAssociationRepository,
    )


def test_service_accepts_injected_repository():
    """Verify repository dependency injection is preserved."""

    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    service = CateringExpenseCostConsumptionService(
        repository=repository,
    )

    assert service.repository is repository


def test_consume_requires_eligible_association():
    """
    Verify consumption requires an existing eligible Catering
    association for the contribution identity.
    """

    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    repository.get_by_contribution_id.return_value = None

    service = CateringExpenseCostConsumptionService(
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="No eligible Catering Expense Cost Association",
    ):
        service.consume(
            _contribution(),
        )

    repository.get_by_contribution_id.assert_called_once_with(
        "expense-17-catering-event-1",
    )

    repository.update.assert_not_called()


def test_consume_marks_eligible_association_consumed():
    """Verify successful consumption marks the association consumed."""

    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    association = Mock(
    spec=CateringExpenseCostAssociation,
    )
    association.status = "ELIGIBLE"
    association.consumed_at = None
    association.mark_consumed.side_effect = (
        lambda consumed_at: (
            setattr(association, "status", "CONSUMED"),
            setattr(association, "consumed_at", consumed_at),
        )
    )

    repository.get_by_contribution_id.return_value = association
    repository.update.return_value = association

    service = CateringExpenseCostConsumptionService(
        repository=repository,
    )

    result = service.consume(
        _contribution(),
    )

    assert result is association
    assert association.status == "CONSUMED"
    assert association.consumed_at is not None
    assert association.consumed_at.tzinfo is not None
    association.mark_consumed.assert_called_once()

    repository.get_by_contribution_id.assert_called_once_with(
        "expense-17-catering-event-1",
    )
    repository.update.assert_called_once_with(
        association,
    )


def test_consume_is_idempotent_for_consumed_association():
    """Verify retrying an already-consumed contribution is harmless."""

    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    association = Mock(
        spec=CateringExpenseCostAssociation,
    )
    association.status = "CONSUMED"

    consumed_at = datetime(
        2026,
        9,
        30,
        13,
        0,
        tzinfo=timezone.utc,
    )
    association.consumed_at = consumed_at

    repository.get_by_contribution_id.return_value = association

    service = CateringExpenseCostConsumptionService(
        repository=repository,
    )

    result = service.consume(
        _contribution(),
    )

    assert result is association
    assert association.status == "CONSUMED"
    assert association.consumed_at is consumed_at

    repository.get_by_contribution_id.assert_called_once_with(
        "expense-17-catering-event-1",
    )
    repository.update.assert_not_called()


def test_consume_rejects_unknown_association_status():
    """Verify an unexpected association state cannot be consumed."""

    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    association = Mock(
        spec=CateringExpenseCostAssociation,
    )
    association.status = "CANCELLED"

    repository.get_by_contribution_id.return_value = association

    service = CateringExpenseCostConsumptionService(
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="Catering Expense Cost Association is not eligible",
    ):
        service.consume(
            _contribution(),
        )

    repository.update.assert_not_called()


def test_consume_does_not_access_expense():
    """
    Verify the Catering consumption boundary operates entirely from
    the immutable integration contribution and Catering association.
    """

    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    association = Mock(
        spec=CateringExpenseCostAssociation,
    )
    association.status = "CONSUMED"

    repository.get_by_contribution_id.return_value = association

    service = CateringExpenseCostConsumptionService(
        repository=repository,
    )

    service.consume(
        _contribution(),
    )

    assert not hasattr(
        service,
        "expense_service",
    )
