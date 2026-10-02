"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Revenue repository.
"""

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.catering.models import CateringRevenue


class CateringRevenueRepository(
    SQLAlchemyRepository[CateringRevenue]
):
    """
    Repository for Catering Revenue records.

    Persistence remains within the Catering bounded module.
    """

    def __init__(self) -> None:
        super().__init__(CateringRevenue)


__all__ = [
    "CateringRevenueRepository",
]
