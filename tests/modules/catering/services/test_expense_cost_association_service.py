"""
Tests for the Catering Expense Cost Association application service.
"""

from unittest.mock import Mock

import pytest

from app.modules.catering.models import CateringExpenseCostAssociation
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import (
    CateringExpenseCostAssociationService,
)


def _association():
    association = Mock(
        spec=CateringExpenseCostAssociation,
    )
    association.expense_id = 42
    association.catering_context_type = "CATERING_EVENT"
    association.catering_context_reference = "EVENT-001"
    association.status = "ELIGIBLE"
    association.contribution_id = "expense-42-event-001"
    association.consumed_at = None
    return association


def _service(
    repository=None,
    authorization_adapter=None,
):
    return CateringExpenseCostAssociationService(
        repository=repository
        or Mock(
            spec=CateringExpenseCostAssociationRepository,
        ),
        authorization_adapter=authorization_adapter
        or Mock(
            spec=CateringAuthorizationAdapter,
        ),
    )


def test_service_uses_default_repository():
    service = CateringExpenseCostAssociationService()

    assert isinstance(
        service.repository,
        CateringExpenseCostAssociationRepository,
    )


def test_service_accepts_injected_repository():
    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    service = CateringExpenseCostAssociationService(
        repository=repository,
    )

    assert service.repository is repository


def test_create_requires_authorization_adapter():
    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )

    service = CateringExpenseCostAssociationService(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create(
            _association(),
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_authorizes_before_persistence():
    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    association = _association()
    repository.add.return_value = association

    service = CateringExpenseCostAssociationService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    subject = Mock()

    result = service.create(
        association,
        subject=subject,
    )

    assert result is association

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.EXPENSE_COST_ASSOCIATION.CREATE",
    )
    repository.add.assert_called_once_with(
        association,
    )


def test_create_denied_does_not_persist():
    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    service = CateringExpenseCostAssociationService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.create(
            _association(),
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_does_not_require_expense_lookup():
    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    association = _association()
    repository.add.return_value = association

    service = CateringExpenseCostAssociationService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.create(
        association,
        subject=Mock(),
    )

    assert result is association
    repository.add.assert_called_once_with(
        association,
    )


def test_create_does_not_change_association_consumption_state():
    repository = Mock(
        spec=CateringExpenseCostAssociationRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    association = _association()
    repository.add.return_value = association

    service = CateringExpenseCostAssociationService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    result = service.create(
        association,
        subject=Mock(),
    )

    assert result is association
    assert association.status == "ELIGIBLE"
    assert association.consumed_at is None

    repository.add.assert_called_once_with(
        association,
    )
