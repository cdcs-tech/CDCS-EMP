"""
CDCS Enterprise Management Platform (CDCS-EMP)

Procurement Module

Tests for the Procurement Finance commitment repository.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.modules.procurement.models import (
    ProcurementFinanceCommitment,
)
from app.modules.procurement.repositories.finance_commitment import (
    ProcurementFinanceCommitmentRepository,
)


def test_repository_uses_procurement_finance_commitment_model():
    """
    The repository must be configured for the commitment model.
    """

    repository = ProcurementFinanceCommitmentRepository()

    assert repository.model is ProcurementFinanceCommitment


def test_get_by_idempotency_key_returns_matching_commitment():
    """
    The repository must retrieve a commitment by its unique
    business-operation identity.
    """

    commitment = MagicMock(
        spec=ProcurementFinanceCommitment
    )

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = commitment

    with patch(
        "app.modules.procurement.repositories.finance_commitment.db.session.execute",
        return_value=execute_result,
    ) as execute:
        repository = ProcurementFinanceCommitmentRepository()

        result = repository.get_by_idempotency_key(
            "procurement-commitment:PO-0001"
        )

    assert result is commitment
    execute.assert_called_once()


def test_get_by_idempotency_key_returns_none_when_not_found():
    """
    The repository must return None when the idempotency key
    does not exist.
    """

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None

    with patch(
        "app.modules.procurement.repositories.finance_commitment.db.session.execute",
        return_value=execute_result,
    ):
        repository = ProcurementFinanceCommitmentRepository()

        result = repository.get_by_idempotency_key(
            "procurement-commitment:DOES-NOT-EXIST"
        )

    assert result is None


def test_get_by_purchase_order_id_returns_matching_commitment():
    """
    The repository must retrieve a commitment by its associated
    Purchase Order.
    """

    commitment = MagicMock(
        spec=ProcurementFinanceCommitment
    )

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = commitment

    with patch(
        "app.modules.procurement.repositories.finance_commitment.db.session.execute",
        return_value=execute_result,
    ) as execute:
        repository = ProcurementFinanceCommitmentRepository()

        result = repository.get_by_purchase_order_id(
            101
        )

    assert result is commitment
    execute.assert_called_once()


def test_get_by_purchase_order_id_returns_none_when_not_found():
    """
    The repository must return None when the Purchase Order
    has no Finance commitment.
    """

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None

    with patch(
        "app.modules.procurement.repositories.finance_commitment.db.session.execute",
        return_value=execute_result,
    ):
        repository = ProcurementFinanceCommitmentRepository()

        result = repository.get_by_purchase_order_id(
            999999999
        )

    assert result is None
