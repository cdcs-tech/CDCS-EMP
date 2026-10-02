"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Module

Finance Revenue repository.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.finance.models import (
    FinanceRevenue,
)


class FinanceRevenueRepository(
    SQLAlchemyRepository[FinanceRevenue],
):
    """
    Repository for Finance Revenue entities.
    """

    def __init__(self) -> None:
        """
        Initialize the Finance Revenue repository.
        """

        super().__init__(
            FinanceRevenue
        )

    def get_by_contribution_reference(
        self,
        contribution_reference: str,
    ) -> Optional[FinanceRevenue]:
        """
        Retrieve a Finance Revenue record by its
        stable business contribution identity.

        The contribution reference is the Finance-side
        idempotency identity for an accepted business
        contribution. It is distinct from an enterprise
        IntegrationRequest request_id.
        """

        statement = select(
            FinanceRevenue
        ).where(
            FinanceRevenue.contribution_reference
            == contribution_reference
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "FinanceRevenueRepository",
]
