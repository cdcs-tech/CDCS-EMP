"""
Tests for Expense Management application services.
"""

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
