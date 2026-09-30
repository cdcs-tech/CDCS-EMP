"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Tests for the Procurement Purchase Requirement repository.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.modules.procurement.models import PurchaseRequirement
from app.modules.procurement.repositories.purchase_requirement import (
    PurchaseRequirementRepository,
)


def test_repository_uses_purchase_requirement_model():
    """
    The repository must be configured for the Purchase Requirement model.
    """

    repository = PurchaseRequirementRepository()

    assert repository.model is PurchaseRequirement


def test_get_by_reference_returns_matching_purchase_requirement():
    """
    The repository must retrieve a Purchase Requirement by its
    unique business reference.
    """

    purchase_requirement = MagicMock(
        spec=PurchaseRequirement
    )

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = (
        purchase_requirement
    )

    with patch(
        "app.modules.procurement.repositories.purchase_requirement.db.session.execute",
        return_value=execute_result,
    ) as execute:
        repository = PurchaseRequirementRepository()

        result = repository.get_by_reference(
            "CATERING-PR-CPR-GUID-001"
        )

    assert result is purchase_requirement
    execute.assert_called_once()


def test_get_by_reference_returns_none_when_not_found():
    """
    The repository must return None when the Purchase Requirement
    reference does not exist.
    """

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None

    with patch(
        "app.modules.procurement.repositories.purchase_requirement.db.session.execute",
        return_value=execute_result,
    ):
        repository = PurchaseRequirementRepository()

        result = repository.get_by_reference(
            "CATERING-PR-DOES-NOT-EXIST"
        )

    assert result is None
