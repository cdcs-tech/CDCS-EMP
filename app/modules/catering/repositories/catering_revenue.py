"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Catering Revenue repository.
"""

from sqlalchemy import false, select

from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.extensions import db
from app.modules.catering.models import (
    CateringRevenue,
)


class CateringRevenueRepository(
    SQLAlchemyRepository[CateringRevenue],
):
    """
    Repository for Catering Revenue records.

    Persistence remains within the Catering bounded module.
    """

    def __init__(self) -> None:
        """
        Initialize the Catering Revenue repository.
        """

        super().__init__(
            CateringRevenue
        )

    def get_recognized_by_event_id(
        self,
        event_id: int,
    ) -> CateringRevenue | None:
        """
        Return the recognized Catering Revenue record for an Event.

        Revenue recognition remains an explicit Catering business
        state; this method only retrieves an already-recognized
        record.
        """

        statement = (
            select(
                CateringRevenue
            )
            .where(
                CateringRevenue.event_id
                == event_id
            )
            .where(
                CateringRevenue.status
                == "RECOGNIZED"
            )
            .where(
                CateringRevenue.is_deleted == false()
            )
        )

        return db.session.execute(
            statement
        ).scalar_one_or_none()


__all__ = [
    "CateringRevenueRepository",
]
