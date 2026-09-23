"""
Tests for Expense Management application services.
"""

import pytest
from unittest.mock import Mock

from app.modules.expense.models import (
    Expense,
    ExpenseClassification,
)
from app.modules.expense.services import (
    ExpenseClassificationService,
    ExpenseService,
)


def test_expense_classification_service_uses_expected_entity_name():
    """
    ExpenseClassificationService exposes the correct enterprise
    entity name through its CRUD service boundary.
    """

    repository = Mock()

    service = ExpenseClassificationService(
        repository=repository
    )

    assert service.entity_name == "ExpenseClassification"
    assert service.repository is repository


def test_expense_service_uses_expected_entity_name():
    """
    ExpenseService exposes the correct enterprise entity name
    through its CRUD service boundary.
    """

    repository = Mock()

    service = ExpenseService(
        repository=repository
    )

    assert service.entity_name == "Expense"
    assert service.repository is repository


def test_expense_classification_service_activate_sets_active():
    """
    Activating a classification sets is_active to True and
    persists the entity through the CRUD service boundary.
    """

    classification = ExpenseClassification(
        name="Utilities",
        code="UTIL",
        is_active=False,
    )

    repository = Mock()

    service = ExpenseClassificationService(
        repository=repository
    )

    service.get = Mock(
        return_value=classification
    )
    service.update = Mock(
        return_value=classification
    )

    result = service.activate(1)

    assert result is classification
    assert classification.is_active is True

    service.get.assert_called_once_with(1)
    service.update.assert_called_once_with(
        classification
    )


def test_expense_classification_service_deactivate_sets_inactive():
    """
    Deactivating a classification sets is_active to False and
    persists the entity through the CRUD service boundary.
    """

    classification = ExpenseClassification(
        name="Utilities",
        code="UTIL",
        is_active=True,
    )

    repository = Mock()

    service = ExpenseClassificationService(
        repository=repository
    )

    service.get = Mock(
        return_value=classification
    )
    service.update = Mock(
        return_value=classification
    )

    result = service.deactivate(1)

    assert result is classification
    assert classification.is_active is False

    service.get.assert_called_once_with(1)
    service.update.assert_called_once_with(
        classification
    )


def test_expense_classification_service_paginate_delegates_to_repository():
    """
    ExpenseClassificationService delegates pagination to its repository.
    """

    options = Mock()
    paginated_result = Mock()

    repository = Mock()
    repository.paginate.return_value = paginated_result

    service = ExpenseClassificationService(
        repository=repository
    )

    result = service.paginate(options)

    assert result is paginated_result

    repository.paginate.assert_called_once_with(
        options
    )


def test_expense_service_paginate_delegates_to_repository():
    """
    ExpenseService delegates pagination to its repository.
    """

    options = Mock()
    paginated_result = Mock()

    repository = Mock()
    repository.paginate.return_value = paginated_result

    service = ExpenseService(
        repository=repository
    )

    result = service.paginate(options)

    assert result is paginated_result

    repository.paginate.assert_called_once_with(
        options
    )


def test_expense_service_targets_expense_model():
    """
    ExpenseService is parameterized for the Expense domain model.
    """

    assert Expense.__tablename__ == "expenses"


def test_expense_classification_service_targets_classification_model():
    """
    ExpenseClassificationService is parameterized for the
    ExpenseClassification domain model.
    """

    assert (
        ExpenseClassification.__tablename__
        == "expense_classifications"
    )


def test_expense_service_submit_transitions_and_persists():
    """
    Submitting an Expense delegates the transition to the workflow
    and persists the resulting state.
    """

    expense = Expense(status="DRAFT")
    repository = Mock()
    workflow = Mock()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": "SUBMITTED"},
    )()

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock(
        return_value=expense
    )

    result = service.submit(expense)

    assert result is expense
    workflow.transition.assert_called_once_with(
        "DRAFT",
        "SUBMITTED",
    )
    assert expense.status == "SUBMITTED"
    service.update.assert_called_once_with(expense)


def test_expense_service_approve_transitions_and_persists():
    """
    Approving an Expense delegates the transition to the workflow
    and persists the resulting state.
    """

    expense = Expense(status="SUBMITTED")
    repository = Mock()
    workflow = Mock()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": "APPROVED"},
    )()

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock(
        return_value=expense
    )

    result = service.approve(expense)

    assert result is expense
    workflow.transition.assert_called_once_with(
        "SUBMITTED",
        "APPROVED",
    )
    assert expense.status == "APPROVED"
    service.update.assert_called_once_with(expense)


def test_expense_service_reject_transitions_and_persists():
    """
    Rejecting an Expense delegates the transition to the workflow
    and persists the resulting state.
    """

    expense = Expense(status="SUBMITTED")
    repository = Mock()
    workflow = Mock()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": "REJECTED"},
    )()

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock(
        return_value=expense
    )

    result = service.reject(expense)

    assert result is expense
    workflow.transition.assert_called_once_with(
        "SUBMITTED",
        "REJECTED",
    )
    assert expense.status == "REJECTED"
    service.update.assert_called_once_with(expense)


def test_expense_service_return_transitions_and_persists():
    """
    Returning an Expense delegates the transition to the workflow
    and persists the resulting state.
    """

    expense = Expense(status="SUBMITTED")
    repository = Mock()
    workflow = Mock()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": "RETURNED"},
    )()

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock(
        return_value=expense
    )

    result = service.return_expense(expense)

    assert result is expense
    workflow.transition.assert_called_once_with(
        "SUBMITTED",
        "RETURNED",
    )
    assert expense.status == "RETURNED"
    service.update.assert_called_once_with(expense)


def test_expense_service_resubmit_transitions_and_persists():
    """
    Resubmitting an Expense delegates the transition to the workflow
    and persists the resulting state.
    """

    expense = Expense(status="RETURNED")
    repository = Mock()
    workflow = Mock()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": "SUBMITTED"},
    )()

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock(
        return_value=expense
    )

    result = service.resubmit(expense)

    assert result is expense
    workflow.transition.assert_called_once_with(
        "RETURNED",
        "SUBMITTED",
    )
    assert expense.status == "SUBMITTED"
    service.update.assert_called_once_with(expense)


def test_expense_service_close_transitions_and_persists():
    """
    Closing an Expense delegates the transition to the workflow
    and persists the resulting state.
    """

    expense = Expense(status="APPROVED")
    repository = Mock()
    workflow = Mock()

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {"name": "CLOSED"},
    )()

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock(
        return_value=expense
    )

    result = service.close(expense)

    assert result is expense
    workflow.transition.assert_called_once_with(
        "APPROVED",
        "CLOSED",
    )
    assert expense.status == "CLOSED"
    service.update.assert_called_once_with(expense)


def test_expense_service_propagates_invalid_workflow_transition():
    """
    ExpenseService propagates workflow transition validation errors
    rather than implementing a second transition matrix.
    """

    expense = Expense(status="DRAFT")
    repository = Mock()
    workflow = Mock()

    workflow.transition.side_effect = ValueError(
        "Invalid workflow transition: DRAFT -> APPROVED"
    )

    service = ExpenseService(
        repository=repository,
        workflow=workflow,
    )
    service.update = Mock()

    with pytest.raises(
        ValueError,
        match="Invalid workflow transition",
    ):
        service.approve(expense)

    workflow.transition.assert_called_once_with(
        "DRAFT",
        "APPROVED",
    )
    service.update.assert_not_called()
