"""
Tests for Catering Customer application services.
"""

from unittest.mock import Mock

from app.modules.catering.models import Customer
from app.modules.catering.services import CustomerService


def test_customer_service_uses_expected_entity_name():
    """
    CustomerService exposes the correct enterprise entity name
    through its CRUD service boundary.
    """

    repository = Mock()

    service = CustomerService(
        repository=repository
    )

    assert service.entity_name == "Customer"
    assert service.repository is repository


def test_customer_service_paginate_delegates_to_repository():
    """
    CustomerService delegates pagination to its repository.
    """

    options = Mock()
    paginated_result = Mock()

    repository = Mock()
    repository.paginate.return_value = paginated_result

    service = CustomerService(
        repository=repository
    )

    result = service.paginate(
        options
    )

    assert result is paginated_result

    repository.paginate.assert_called_once_with(
        options
    )


def test_customer_service_activate_sets_active():
    """
    Activating a Customer sets status to ACTIVE and persists
    the entity through the CRUD service boundary.
    """

    customer = Customer(
        name="Test Customer",
        customer_type="INDIVIDUAL",
        status="INACTIVE",
    )

    repository = Mock()

    service = CustomerService(
        repository=repository
    )

    service.get = Mock(
        return_value=customer
    )

    service.update = Mock(
        return_value=customer
    )

    result = service.activate(
        1
    )

    assert result is customer
    assert customer.status == "ACTIVE"

    service.get.assert_called_once_with(
        1
    )

    service.update.assert_called_once_with(
        customer
    )


def test_customer_service_deactivate_sets_inactive():
    """
    Deactivating a Customer sets status to INACTIVE and persists
    the entity through the CRUD service boundary.
    """

    customer = Customer(
        name="Test Customer",
        customer_type="INDIVIDUAL",
        status="ACTIVE",
    )

    repository = Mock()

    service = CustomerService(
        repository=repository
    )

    service.get = Mock(
        return_value=customer
    )

    service.update = Mock(
        return_value=customer
    )

    result = service.deactivate(
        1
    )

    assert result is customer
    assert customer.status == "INACTIVE"

    service.get.assert_called_once_with(
        1
    )

    service.update.assert_called_once_with(
        customer
    )


def test_customer_service_targets_customer_model():
    """
    CustomerService is parameterized for the Customer domain model.
    """

    assert Customer.__tablename__ == "customers"
