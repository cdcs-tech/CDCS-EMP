"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Tests for the Finance Revenue repository.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.modules.finance.models import (
    FinanceRevenue,
)
from app.modules.finance.repositories.finance_revenue import (
    FinanceRevenueRepository,
)


def test_repository_uses_finance_revenue_model():
    """
    The repository must be configured for the Finance Revenue model.
    """

    repository = FinanceRevenueRepository()

    assert repository.model is FinanceRevenue


def test_get_by_contribution_reference_returns_matching_revenue():
    """
    The repository must retrieve a Finance Revenue by its
    stable contribution identity.
    """

    revenue = MagicMock(
        spec=FinanceRevenue
    )

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = revenue

    with patch(
        "app.modules.finance.repositories.finance_revenue.db.session.execute",
        return_value=execute_result,
    ) as execute:
        repository = FinanceRevenueRepository()

        result = repository.get_by_contribution_reference(
            "catering-revenue:CAT-REV-0001"
        )

    assert result is revenue
    execute.assert_called_once()


def test_get_by_contribution_reference_returns_none_when_not_found():
    """
    The repository must return None when the contribution
    reference does not exist.
    """

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = None

    with patch(
        "app.modules.finance.repositories.finance_revenue.db.session.execute",
        return_value=execute_result,
    ):
        repository = FinanceRevenueRepository()

        result = repository.get_by_contribution_reference(
            "catering-revenue:DOES-NOT-EXIST"
        )

    assert result is None
