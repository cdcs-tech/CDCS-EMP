"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module Tests

Purchase requirement repository and service tests.
"""

from unittest.mock import Mock

from app.core.data import QueryOptions
from app.modules.procurement.models import PurchaseRequirement
from app.modules.procurement.repositories import (
    PurchaseRequirementRepository,
)
from app.modules.procurement.services import (
    PurchaseRequirementService,
)


def test_purchase_requirement_repository_targets_correct_model():
    repository = PurchaseRequirementRepository()

    assert repository.model is PurchaseRequirement


def test_purchase_requirement_service_uses_default_repository():
    service = PurchaseRequirementService()

    assert isinstance(
        service.repository,
        PurchaseRequirementRepository,
    )


def test_purchase_requirement_service_accepts_injected_repository():
    repository = Mock(
        spec=PurchaseRequirementRepository,
    )

    service = PurchaseRequirementService(
        repository=repository,
    )

    assert service.repository is repository


def test_purchase_requirement_service_has_correct_entity_name():
    service = PurchaseRequirementService()

    assert service.entity_name == "PurchaseRequirement"


def test_purchase_requirement_service_paginate_delegates_to_repository():
    repository = Mock(
        spec=PurchaseRequirementRepository,
    )

    expected_result = Mock()
    repository.paginate.return_value = expected_result

    service = PurchaseRequirementService(
        repository=repository,
    )

    options = QueryOptions(
        page=1,
        page_size=20,
    )

    result = service.paginate(
        options,
    )

    repository.paginate.assert_called_once_with(
        options,
    )
    assert result is expected_result
